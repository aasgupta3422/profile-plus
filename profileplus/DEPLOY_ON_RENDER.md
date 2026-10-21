# Deploy Profile+ on Render

## Quick deployment
1. Create a GitHub repository and upload all files in this folder.
2. Sign in at https://render.com and choose **New + → Web Service**.
3. Connect your GitHub repository.
4. Choose the Python runtime if asked. Use these settings (also supplied in `render.yaml`):
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
5. Add an environment variable named `SECRET_KEY` with a long random value if Render has not generated it from `render.yaml`.
6. Click **Create Web Service** and wait for the deployment to finish. Render will show the public `https://...onrender.com` URL; open that URL on your phone.

## Important notes
- The app uses SQLite. On hosts with an ephemeral filesystem, user accounts may be lost when the service is redeployed or restarted. For persistent accounts, attach a persistent disk and set `DATABASE_PATH` to a path on that disk (for example `/var/data/resume_builder.db`), or migrate to a managed database.
- `SECRET_KEY` should be a private, random value in the host's environment settings. Do not commit a real secret to GitHub.
- Test signup, login, resume preview, and PDF download after deployment.
