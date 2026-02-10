#!/bin/bash

# Trimora PyPI Upload Script
# Author: Govind Mangropa | Molynex Lab

echo "═══════════════════════════════════════════════════════════════"
echo "  📦 TRIMORA - PyPI Upload Process"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check if build environment exists
if [ ! -d "build_env" ]; then
    echo "❌ Build environment not found. Please run build first."
    exit 1
fi

# Check if dist files exist
if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
    echo "❌ No distribution files found. Please run build first."
    exit 1
fi

echo "📦 Distribution files ready:"
ls -lh dist/
echo ""

# Ask user which repository
echo "Select upload destination:"
echo "  1) Test PyPI (recommended first)"
echo "  2) Production PyPI"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "🧪 Uploading to TEST PyPI..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "When prompted:"
        echo "  Username: __token__"
        echo "  Password: [Your Test PyPI API token]"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        build_env/bin/python -m twine upload --repository testpypi dist/*
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Upload successful!"
            echo ""
            echo "View at: https://test.pypi.org/project/trimora/"
            echo ""
            echo "To test installation:"
            echo "  pip install --index-url https://test.pypi.org/simple/ \\"
            echo "              --extra-index-url https://pypi.org/simple/ \\"
            echo "              trimora"
        fi
        ;;
    2)
        echo ""
        echo "🚀 Uploading to PRODUCTION PyPI..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "⚠️  WARNING: This will publish to the REAL Python Package Index!"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        read -p "Are you sure? (yes/no): " confirm
        
        if [ "$confirm" == "yes" ]; then
            echo ""
            echo "When prompted:"
            echo "  Username: __token__"
            echo "  Password: [Your PyPI API token]"
            echo ""
            build_env/bin/python -m twine upload dist/*
            
            if [ $? -eq 0 ]; then
                echo ""
                echo "🎉 SUCCESS! Trimora is now on PyPI!"
                echo ""
                echo "View at: https://pypi.org/project/trimora/"
                echo ""
                echo "Anyone can now install with:"
                echo "  pip install trimora"
                echo ""
                echo "═══════════════════════════════════════════════════════════════"
                echo "  🎊 Congratulations, Govind! Package published!"
                echo "  🏆 Molynex Lab proudly presents: trimora"
                echo "═══════════════════════════════════════════════════════════════"
            fi
        else
            echo "❌ Upload cancelled."
        fi
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac
