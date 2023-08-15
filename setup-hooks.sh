#!/bin/sh

cat <<EOF > .git/hooks/pre-commit
#!/bin/sh

# Run formatter
pdm run black --check src tests
EOF

chmod +x .git/hooks/pre-commit
