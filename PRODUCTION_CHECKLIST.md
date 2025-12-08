# Production Deployment Checklist

## Prerequisites
- [ ] **PostgreSQL**: Install PostgreSQL for production database.
- [ ] **Nginx/Apache**: Reverse proxy setup is recommended.
- [ ] **Domain & SSL**: Secure your application with HTTPS.

## Backend Setup
1.  **Database**: Update `.env` to use PostgreSQL.
    ```env
    DATABASE_URL=postgresql://user:password@localhost/natpudan_db
    ```
2.  **Dependencies**: Install production dependencies.
    ```bash
    pip install -r backend/requirements.txt
    ```
3.  **Run with Gunicorn**: Use Gunicorn for production performance (Linux/Mac).
    ```bash
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
    ```
    *Note: On Windows, continue using Uvicorn directly or use a process manager like NSSM.*

## Frontend Setup
1.  **Build**: Create optimized production build.
    ```bash
    npm run build
    ```
2.  **Serve**: Serve the `dist` folder using Nginx/Apache or a static file server.

## Security
- [ ] **Secret Keys**: Rotate `SECRET_KEY` in `.env`.
- [ ] **Debug Mode**: Ensure `DEBUG=False` (if applicable) and no sensitive data is logged.
- [ ] **Firewall**: Configure firewall to only allow traffic on necessary ports (80/443).
