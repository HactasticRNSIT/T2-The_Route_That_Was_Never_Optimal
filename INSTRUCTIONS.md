# BioRoute — Role-Based Demo

## Login credentials

### Admin
- Username: `admin`
- Password: `admin`
- Opens `/admin.html`
- Admin can access only:
  - Dashboard
  - Citizen Reports
  - Route Plan
  - Trucks

### User
- Username: `user`
- Password: `user`
- Opens `/report.html`
- User can access only:
  - Report Submission
  - Camera verification
  - Geotagging

## Run steps

```bash
cd D:\Saipranav\BioRoute\backend
npm install
npm start
```

Open:

```text
http://localhost:3000
```

## Demo sequence

1. Login as `user / user`.
2. Submit a waste report using camera verification and location.
3. Logout.
4. Login as `admin / admin`.
5. Open Citizen Reports and verify the pending report.
6. Open Route Plan and click Run Optimization.
7. Select/start a truck route and show the simulation.
