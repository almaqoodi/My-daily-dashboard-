# My Daily Dashboard V3

## Deploy to Render
1. Create a GitHub repository and upload **the files inside this folder** to its root.
2. Render Dashboard → New + → Blueprint → Connect repository → Apply.
3. After deploy completes, open the `onrender.com` URL on your phone.
4. iPhone Safari → Share → Add to Home Screen. Samsung Chrome → menu → Add to Home screen / Install app.

The RSS endpoint `/api/news` fetches Google News RSS and caches it for 15 minutes. Internet access required. Weather, commodity prices, and the 9 AM scheduled refresh are **not implemented**. On Render free service, idle spin-down can cause delayed first load; availability depends on plan and platform policies. No login is configured, so anyone with the URL can view the dashboard. The app shell may cache offline but live news requires connectivity.
