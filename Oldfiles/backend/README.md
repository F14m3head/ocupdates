# backend

This is the backend for ocUpdates

## How to run
> Make sure the `shared` package is installed in editable mode from the project root (should've already done it before navigating here).

> Make sure you're in the ``\backend`` directory.

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Run
1. Navigate back to the project root:
    ```bash
    cd ..
    ```
2. Run the app
    ```bash
    python -m uvicorn backend.app.main:app --reload
    ```
    <sub>the "--reload" flag makes the backend server automatically restart when a change is made to it (very useful for development)</sub>