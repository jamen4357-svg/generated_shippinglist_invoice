"# Invoice Generation Streamlit App

A comprehensive invoice and packing list generation system built with Streamlit.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows/Linux/Mac

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd GENERATE_INVOICE_STREAMLIT_WEB
   ```

2. **Activate the virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Run the application:**
   ```bash
   # 🎯 Windows (RECOMMENDED - just double-click!)
   Double-click "Run Invoice App.lnk"

   # Windows from network share (UNC path)
   .\run_app.ps1

   # Or manually:
   venv\Scripts\activate
   streamlit run app.py

   # Linux/Mac
   ./run_app.sh

   # Or manually:
   source venv/bin/activate
   streamlit run app.py
   ```

4. **Access the app:**
   Open your browser to `http://localhost:8501`

## 🌐 Network Share Deployment

This application is designed to work from network shares (UNC paths) without installation:

### For Windows Users:
1. **Copy the entire folder** to your network share (e.g., `\\server\shared\apps\`)
2. **Double-click** `Run Invoice App.lnk` - it automatically handles UNC paths
3. The app will map a network drive if needed and start Streamlit

### For IT Administrators:
- No installation required on user machines
- All dependencies are included in the `venv/` folder
- Users only need Python installed (which comes with Windows 10+)
- The shortcut handles virtual environment activation automatically

### Creating Additional Shortcuts:
```powershell
# Run from the app directory to create a new shortcut
.\create_shortcut.ps1
```

## 📦 What's Included

This project comes with a pre-configured virtual environment containing all necessary dependencies:

- **Streamlit** - Web app framework
- **Pandas** - Data manipulation
- **OpenPyXL** - Excel file handling
- **Plotly** - Data visualization
- **Streamlit extras** - Additional Streamlit components

## 🛠️ Development

### Adding New Dependencies

1. Add the package to `requirements.txt`
2. Install in the virtual environment:
   ```bash
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

### Project Structure

```
├── app.py                 # Main Streamlit application
├── pages/                 # Streamlit pages
├── data/                  # Application data and databases
├── invoice_gen/           # Invoice generation logic
├── config_template_cli/   # Configuration tools
├── requirements.txt       # Python dependencies
├── venv/                  # Virtual environment (pre-configured)
├── run_app.bat           # Windows CMD launcher script
├── run_app.ps1           # Windows PowerShell launcher (handles UNC paths)
├── run_app.sh            # Linux/Mac launcher script
├── Run Invoice App.lnk   # Windows shortcut (easiest way to run)
├── create_shortcut.ps1   # Script to create additional shortcuts
└── README.md             # This file
```

## 🔧 Troubleshooting

### Virtual Environment Issues
If the virtual environment doesn't work:

```bash
# Delete and recreate
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Windows Shortcut (Easiest Option)

1. **Copy the shortcut file** `Run Invoice App.lnk` to your network share or desktop
2. **Double-click** the shortcut to run the application
3. The shortcut automatically handles UNC paths and virtual environment activation

**To create additional shortcuts:**
```powershell
# Run this script to create a new shortcut
.\create_shortcut.ps1
```

## 📋 Features

- User authentication and authorization
- Invoice generation from Excel templates
- Packing list creation
- Database management
- Admin dashboard
- Activity logging

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

This project is proprietary software.
