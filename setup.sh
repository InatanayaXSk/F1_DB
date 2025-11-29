#!/bin/bash

# F1 Prediction System Setup Script (Updated for PostgreSQL + Redis)

echo "=========================================="
echo "F1 Prediction System Setup"
echo "=========================================="
echo ""

echo "⚠️  IMPORTANT: This system now requires PostgreSQL and Redis"
echo ""
echo "Please use one of the following setup methods:"
echo ""
echo "1. Automated setup (recommended):"
echo "   python setup.py"
echo ""
echo "2. Manual setup with Docker:"
echo "   docker-compose up -d"
echo "   pip install -r requirements.txt"
echo "   python src/database.py"
echo ""
echo "3. See MIGRATION.md for detailed instructions"
echo ""
echo "=========================================="
echo ""
