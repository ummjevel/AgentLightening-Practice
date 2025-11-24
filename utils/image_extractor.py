"""Image extraction utilities from PDFs."""

import fitz  # PyMuPDF
import logging
from typing import List, Dict, Any, Tuple
from pathlib import Path
from PIL import Image
import io


logger = logging.getLogger(__name__)


class ImageExtractor:
    """Extract images from PDF files."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ImageExtractor.

        Args:
            config: Configuration dictionary for image extraction settings
        """
        self.max_images = config.get('max_images_per_paper', 3)
        self.image_format = config.get('image_format', 'png')
        self.image_quality = config.get('image_quality', 85)
        self.min_width = config.get('min_image_width', 300)
        self.min_height = config.get('min_image_height', 300)

        logger.info("Initialized ImageExtractor")

    def extract_images(self, pdf_path: str, output_dir: str, paper_id: str) -> List[str]:
        """
        Extract images from PDF and save to output directory.

        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save extracted images
            paper_id: Unique identifier for the paper (used in filenames)

        Returns:
            List of paths to extracted image files
        """
        logger.info(f"Extracting images from: {pdf_path}")

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        try:
            doc = fitz.open(pdf_path)
            image_paths = []
            image_count = 0

            for page_num in range(len(doc)):
                if image_count >= self.max_images:
                    break

                page = doc[page_num]
                image_list = page.get_images()

                for img_index, img_info in enumerate(image_list):
                    if image_count >= self.max_images:
                        break

                    try:
                        xref = img_info[0]
                        base_image = doc.extract_image(xref)

                        if base_image:
                            image_bytes = base_image["image"]
                            image_ext = base_image["ext"]

                            # Load image with PIL to check dimensions
                            img = Image.open(io.BytesIO(image_bytes))

                            # Filter by size
                            if img.width >= self.min_width and img.height >= self.min_height:
                                # Save image
                                filename = f"{paper_id}_img_{image_count + 1}.{self.image_format}"
                                filepath = Path(output_dir) / filename

                                # Convert and save
                                if img.mode in ('RGBA', 'LA', 'P'):
                                    # Convert to RGB for formats that don't support transparency
                                    if self.image_format.lower() in ['jpg', 'jpeg']:
                                        background = Image.new('RGB', img.size, (255, 255, 255))
                                        if img.mode == 'P':
                                            img = img.convert('RGBA')
                                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                                        img = background

                                img.save(
                                    filepath,
                                    format=self.image_format.upper(),
                                    quality=self.image_quality if self.image_format.lower() in ['jpg', 'jpeg'] else None
                                )

                                image_paths.append(str(filepath))
                                image_count += 1

                                logger.info(f"Extracted image {image_count}: {filename} ({img.width}x{img.height})")

                    except Exception as e:
                        logger.warning(f"Error extracting image {img_index} from page {page_num}: {e}")
                        continue

            doc.close()

            logger.info(f"Successfully extracted {len(image_paths)} images")

            return image_paths

        except Exception as e:
            logger.error(f"Error extracting images from PDF: {e}")
            return []

    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """
        Get information about an image file.

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with image information
        """
        try:
            img = Image.open(image_path)
            return {
                'path': image_path,
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'size_bytes': Path(image_path).stat().st_size,
            }
        except Exception as e:
            logger.error(f"Error getting image info: {e}")
            return {}
