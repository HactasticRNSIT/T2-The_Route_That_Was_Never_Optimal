# Waste Management + BioRoute Integration

## What Changed
- The Admin Portal login in the Waste Management app now redirects directly to the BioRoute dashboard.
- The old admin dashboard view was removed from the post-login flow.
- BioRoute frontend files were integrated into the Vite app using the `public/bioroute` directory.

## Login Credentials
- Username: admin
- Password: admin123

## How to Run

### 1. Open terminal
Navigate to the project folder:

```bash
cd waste-management
```

### 2. Install dependencies

```bash
npm install
```

### 3. Start the frontend

```bash
npm run dev
```

### 4. Open in browser
Vite will show a local URL similar to:

```bash
http://localhost:5173
```

Open it in the browser.

## Flow
1. Open homepage
2. Go to "Admin Portal"
3. Login using admin/admin123
4. You will automatically be redirected to the BioRoute website

## BioRoute Location
Integrated files are stored in:

```bash
public/bioroute
```
