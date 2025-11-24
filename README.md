# arXiv Paper Summarizer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

> *An intelligent agent system that automatically collects, summarizes, and visualizes the latest academic papers from arXiv using AI, with optional Agent Lightning integration for continuous optimization.*

[한국어 문서](README.ko.md) | **English**

---

## 🎯 Key Features

- ✅ **Automated Paper Collection**: Fetch the latest papers from arXiv API
- ✅ **AI-Powered Summarization**: Structured summaries using SKT-AI A.X-4.0 LLM
- ✅ **Smart Image Extraction**: Automatically extract key figures from PDFs
- ✅ **Beautiful HTML Reports**: Generate visual reports with embedded images
- ✅ **Configuration Management**: Centralized YAML configuration (zero hardcoded values)
- ⚡ **Agent Lightning Integration**: Track and optimize agent performance with RL

---

## 📐 Architecture

This project implements a multi-agent architecture inspired by [Agent Lightning](https://github.com/microsoft/agent-lightning):

```
┌─────────────────────────────────────────────────────────┐
│             arXiv Paper Summarizer System               │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Fetcher    │  │ Summarizer   │  │  Presenter   │
│   Agent      │  │   Agent      │  │    Agent     │
│              │  │  (w/ AL*)    │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
    arXiv API         LLM (A.X-4.0)      HTML Report
                                         + Images

* AL = Agent Lightning tracking
```

### Agent Descriptions

| Agent | Responsibility | Key Features |
|-------|---------------|--------------|
| **Fetcher** | Paper collection & extraction | Downloads PDFs, extracts text & images |
| **Summarizer** | AI-powered summarization | Generates structured summaries with LLM |
| **Presenter** | Report generation | Creates beautiful HTML reports |

---

## 📁 Project Structure

```
arxiv-paper-summarizer/
├── agents/                      # Agent modules
│   ├── __init__.py
│   ├── fetcher.py              # Paper collection agent
│   ├── summarizer.py           # Summarization agent (with AL tracking)
│   └── presenter.py            # Report generation agent
├── utils/                       # Utility modules
│   ├── __init__.py
│   ├── config_loader.py        # YAML configuration loader
│   ├── arxiv_client.py         # arXiv API client
│   ├── pdf_processor.py        # PDF text extraction
│   ├── image_extractor.py      # PDF image extraction
│   └── agent_lightning_tracker.py  # Agent Lightning integration
├── templates/                   # HTML templates
│   └── summary_report.html     # Report template
├── config/                      # Configuration files
│   └── config.yaml             # Main configuration
├── data/                        # Data storage
│   ├── papers/                 # Downloaded PDFs
│   ├── images/                 # Extracted images
│   ├── summaries/              # Generated reports
│   └── lightning_store/        # Agent Lightning tracking data
├── main.py                      # Main entry point
├── requirements.txt             # Python dependencies
├── README.md                    # English documentation
└── README.ko.md                 # Korean documentation
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/arxiv-paper-summarizer.git
cd arxiv-paper-summarizer

# Install dependencies
pip install -r requirements.txt
```

### Configuration

All settings are managed in `config/config.yaml`:

```yaml
# arXiv settings
arxiv:
  category: "eess.AS"        # Paper category
  max_results: 10            # Number of papers to fetch

# LLM settings (SKT-AI A.X-4.0)
llm:
  api_key: "your-api-key"    # API key
  model: "ax4"               # Model name
  temperature: 0.7           # Generation temperature

# Agent Lightning settings (optional)
agent_lightning:
  enabled: false             # Enable/disable tracking
  track_prompts: true
  track_responses: true
  track_rewards: true
```

### Running

```bash
python main.py
```

**Note**: The arXiv API may occasionally have rate limiting or temporary access restrictions. If you encounter HTTP 403 errors, try again after a few minutes or from a different network.

---

## ⚡ Agent Lightning Integration

This project includes optional [Agent Lightning](https://github.com/microsoft/agent-lightning) integration for optimizing agent performance through reinforcement learning.

### What is Agent Lightning?

Agent Lightning is Microsoft's framework for optimizing AI agents with minimal code changes. It provides:

- **Automatic tracking** of prompts, responses, and rewards
- **Reinforcement learning** for iterative improvement
- **Prompt optimization** using various algorithms
- **Framework-agnostic** design (works with any agent framework)

### Enabling Agent Lightning

1. **Install Agent Lightning** (uncomment in `requirements.txt`):
   ```bash
   pip install agentlightning
   ```

2. **Enable in configuration** (`config/config.yaml`):
   ```yaml
   agent_lightning:
     enabled: true
     store_path: "data/lightning_store"
     track_prompts: true
     track_responses: true
     track_rewards: true
     optimization_algorithm: "rl"
   ```

3. **Run the system**:
   ```bash
   python main.py
   ```

### How It Works

The **SummarizerAgent** includes Agent Lightning tracking:

```python
# Track prompt
event_id = tracker.emit_prompt(
    agent_name="SummarizerAgent",
    prompt=prompt,
    metadata={'paper_id': paper_id, 'model': self.model}
)

# Track response
tracker.emit_response(
    event_id=event_id,
    response=summary_text,
    metadata={'tokens_used': tokens}
)

# Track reward (based on quality heuristics)
tracker.emit_reward(
    event_id=event_id,
    reward=0.8,
    reason="Good summary length and structure"
)
```

### Tracked Data

All tracking data is saved to `data/lightning_store/session_*.json`:

```json
{
  "session_id": "20241124_120000",
  "total_events": 42,
  "events": [
    {
      "event_type": "prompt",
      "agent_name": "SummarizerAgent",
      "prompt": "...",
      "metadata": {...}
    },
    {
      "event_type": "response",
      "response": "...",
      "metadata": {...}
    },
    {
      "event_type": "reward",
      "reward": 0.8,
      "reason": "..."
    }
  ]
}
```

---

## 📋 Configuration Guide

### arXiv Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `category` | arXiv category code | `eess.AS` |
| `max_results` | Number of papers to fetch | `10` |
| `sort_by` | Sort criterion | `submittedDate` |

**Popular Categories**:
- `cs.AI` - Artificial Intelligence
- `cs.CV` - Computer Vision
- `cs.CL` - Computation and Language
- `eess.AS` - Audio and Speech Processing

### LLM Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `api_key` | SKT-AI API key | Required |
| `base_url` | API endpoint | `https://guest-api.sktax.chat/v1` |
| `model` | Model name | `ax4` |
| `temperature` | Generation temperature | `0.7` |
| `max_tokens` | Maximum response tokens | `2000` |

### PDF Processing Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `max_images_per_paper` | Images to extract per paper | `3` |
| `image_format` | Output image format | `png` |
| `min_image_width` | Minimum image width | `300` |
| `min_image_height` | Minimum image height | `300` |

---

## 📊 Output Example

Generated HTML reports include:

### 1. Paper Metadata
- Title, authors, submission date
- arXiv ID with direct link
- Categories

### 2. Structured Summary
- 📋 **Key Highlights**: 2-3 sentence overview
- 🎯 **Research Objective**: Problem being solved
- 🔬 **Methodology**: Core techniques used
- 📊 **Main Results**: Key findings
- 💡 **Significance & Impact**: Academic/practical value

### 3. Key Figures
- 2-3 main figures extracted from PDF
- Captions for each figure

**Example output**: `data/summaries/2024-11-24-arxiv-summary.html`

---

## 🛠️ Development

### Adding a New Category

Edit `config/config.yaml`:

```yaml
arxiv:
  category: "cs.AI"  # Change to desired category
```

### Customizing Templates

Modify `templates/summary_report.html` to change the report design.

### Logging

Configure logging in `config/config.yaml`:

```yaml
logging:
  level: "DEBUG"  # DEBUG, INFO, WARNING, ERROR
  file: "arxiv_summarizer.log"
```

---

## 🧪 Testing

```bash
# Run with test configuration (2 papers)
# Set max_results: 2 in config.yaml
python main.py

# Check output
ls data/summaries/
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [arXiv](https://arxiv.org/) - Open access pre-print repository
- [SKT-AI](https://github.com/SKT-AI/A.X-4.0) - A.X-4.0 LLM API provider
- [Agent Lightning](https://github.com/microsoft/agent-lightning) - AI agent optimization framework
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF processing library

---

## 📞 Support

- Issues: [GitHub Issues](https://github.com/yourusername/arxiv-paper-summarizer/issues)
- Documentation: [Wiki](https://github.com/yourusername/arxiv-paper-summarizer/wiki)

---

## 🗺️ Roadmap

- [ ] Support for multiple LLM providers (OpenAI, Claude, etc.)
- [ ] Multi-language summary support
- [ ] Email notification for daily digests
- [ ] Web interface for configuration
- [ ] Full Agent Lightning optimization pipeline
- [ ] Docker containerization

---

Made with ❤️ by the community
