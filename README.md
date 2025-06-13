# BatchCut - AI-Powered Image Processing Tool

Little Image processing tool for Trendsi

## Features

### 🎯 Face Detection & Cropping
- **Automatic Face Detection**: Uses OpenCV's DNN face detection model for accurate face recognition
- **Smart Cropping**: Automatically crops images from the chin area downward
- **Customizable Parameters**: Adjust confidence threshold and cropping percentage
- **Batch Processing**: Process entire folders of images at once

### 🤖 AI Background Removal
- **U2NET Model**: Leverages the powerful U2NET deep learning model for precise background removal
- **Multi-pass Processing**: Applies multiple iterations for cleaner results
- **White Background**: Automatically adds clean white background to processed images
- **High Quality Output**: Maintains image quality throughout the processing pipeline

### ⚙️ Flexible Configuration
- **Custom Output Size**: Set target dimensions (default: 1350x1800)
- **DPI Control**: Configure output DPI settings (default: 300,300)
- **Quality Settings**: Adjustable JPEG quality for optimal file size/quality balance
- **Real-time Preview**: Preview processed images before saving

## Installation

### Download Pre-built Executable (Recommended)
1. Go to the [Releases](https://github.com/Yuchen971/Yuchen971-Image-cut-mat-with-ai/releases) page
2. Download the latest `BatchCut.exe` for Windows
3. Run the executable directly - no installation required!

### Build from Source
```bash
# Clone the repository
git clone https://github.com/Yuchen971/Yuchen971-Image-cut-mat-with-ai.git
cd Yuchen971-Image-cut-mat-with-ai

# Install dependencies
pip install -r requirements.txt

# Run the application
python auto_cut_and_mat_image/main.py
```

## Usage

### Face Detection & Cropping Tab
1. **Set Parameters**:
   - Target Size: Enter desired output dimensions (e.g., "1350x1800")
   - DPI: Set output DPI (e.g., "300,300")
   - Confidence: Face detection confidence threshold (0.0-1.0)
   - Cut Percentage: How much of the face area to include in cropping (%)

2. **Process Images**:
   - **Single Image**: Click "单个处理" to process one image with preview
   - **Batch Processing**: Click "批量处理" to process entire folders

### AI Background Removal Tab
1. **Configure Output**:
   - Set target dimensions and DPI settings
   
2. **Process Images**:
   - **Single Image**: Process with real-time preview
   - **Batch Processing**: Process multiple images automatically

## Technical Details

### Models Used
- **Face Detection**: OpenCV DNN with SSD MobileNet architecture
- **Background Removal**: U2NET (U-Square Network) for salient object detection
- **Image Processing**: PIL/Pillow for high-quality image manipulation

### Supported Formats
- **Input**: JPEG, PNG
- **Output**: JPEG with configurable quality and DPI

### Performance Features
- **Lazy Loading**: Models are loaded on-demand to reduce startup time
- **Multi-threading**: Background model loading for better user experience
- **Memory Optimization**: Efficient memory management for batch processing
- **Progress Tracking**: Real-time progress bars for batch operations

## System Requirements

- **Operating System**: Windows 10/11 (64-bit)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free space for models and temporary files
- **Graphics**: No special GPU requirements (CPU-based processing)

## Development

### Project Structure
```
auto_cut_and_mat_image/
├── main.py              # Main application entry point
├── engine_lazy.py       # AI processing engine with lazy loading
├── splash_screen.py     # Startup splash screen
├── app_icon.ico         # Application icon
├── u2net/              # U2NET model implementation
│   ├── model.py        # Neural network architecture
│   └── utils.py        # Utility functions
└── ckpt/               # Model checkpoints directory
```

### Building Executable
The project includes automated GitHub Actions workflow for building Windows executables:

```yaml
# Triggered on push to master branch
# Automatically downloads required models
# Builds standalone executable with PyInstaller
# Creates GitHub release with downloadable exe
```

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- **U2NET**: Thanks to the authors of U2NET for the excellent background removal model
- **OpenCV**: For providing robust computer vision tools
- **PyTorch**: For the deep learning framework
- **PIL/Pillow**: For image processing capabilities

## Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/Yuchen971/Yuchen971-Image-cut-mat-with-ai/issues) page
2. Create a new issue with a detailed description, and I probably won't reply
3. Include system information and error messages if applicable
