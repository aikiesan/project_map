# 🚀 CP2B Maps V2 - Deployment Guide

**Last Updated:** September 30, 2025
**Platform:** Streamlit Community Cloud
**Status:** Production Ready ✅

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Steps](#deployment-steps)
3. [Configuration](#configuration)
4. [Troubleshooting](#troubleshooting)
5. [Post-Deployment](#post-deployment)

---

## 🔧 Prerequisites

### **Required Accounts**
- ✅ GitHub account (repository owner)
- ✅ Streamlit Community Cloud account (free at [share.streamlit.io](https://share.streamlit.io))

### **Repository Requirements**
- ✅ All code pushed to GitHub
- ✅ `requirements.txt` with all dependencies
- ✅ `packages.txt` for system dependencies
- ✅ `.streamlit/config.toml` for configuration
- ✅ Data files committed (database, shapefiles, rasters)

### **Data Files Checklist**
- ✅ `data/database/cp2b_maps.db` (645 municipalities)
- ✅ `data/shapefile/*.shp` (6 GIS layers)
- ✅ `data/rasters/mapbiomas_agropecuaria_sp_2024.tif` (13.5 MB)

---

## 🚀 Deployment Steps

### **Step 1: Prepare Repository**

1. **Verify all files are committed:**
   ```bash
   git status
   git add .
   git commit -m "Prepare for production deployment"
   git push origin main
   ```

2. **Ensure data files are in repository:**
   - Data files should be committed (total ~20-30 MB is acceptable for Streamlit Cloud)
   - If data files exceed 100 MB, consider Git LFS or external storage

### **Step 2: Connect to Streamlit Cloud**

1. **Go to [share.streamlit.io](https://share.streamlit.io)**

2. **Sign in with GitHub**
   - Authorize Streamlit to access your repositories

3. **Create New App:**
   - Click "New app" button
   - Select repository: `aikiesan/cp2b_maps_v2`
   - Select branch: `main`
   - Main file path: `app.py`
   - App URL: Choose a custom subdomain (e.g., `cp2b-maps-v2.streamlit.app`)

### **Step 3: Configure Deployment**

1. **Advanced Settings (Optional):**
   - Python version: `3.11` (recommended)
   - No secrets needed for this app (uses local data files)

2. **Click "Deploy!"**
   - Initial deployment takes 5-10 minutes
   - Streamlit Cloud will:
     - Install system packages from `packages.txt`
     - Install Python packages from `requirements.txt`
     - Start the application

### **Step 4: Monitor Deployment**

Watch the deployment logs for:
- ✅ Package installation success
- ✅ Application startup
- ✅ Data file loading
- ⚠️ Any errors or warnings

---

## ⚙️ Configuration

### **Streamlit Configuration (`.streamlit/config.toml`)**

Already configured for production with:
- Professional theme (WCAG 2.1 Level A compliant)
- Performance optimization
- Security settings (XSRF protection, CORS disabled)
- 100 MB max upload size

### **Environment Variables (Optional)**

If needed, add secrets in Streamlit Cloud dashboard:
1. Go to app settings
2. Navigate to "Secrets" section
3. Add TOML-formatted secrets:
   ```toml
   [database]
   host = "your-host"

   [api_keys]
   mapbox_token = "your-token"
   ```

### **System Dependencies (`packages.txt`)**

Pre-configured for geospatial libraries:
- GDAL (Geospatial Data Abstraction Library)
- GEOS (Geometry Engine)
- PROJ (Cartographic Projections)
- Rasterio dependencies

---

## 🔍 Troubleshooting

### **Common Issues & Solutions**

#### **1. "Module not found" Error**
**Cause:** Missing dependency in `requirements.txt`
**Solution:**
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

#### **2. "No such file or directory" - Data Files**
**Cause:** Data files not committed or wrong path
**Solution:**
- Check file paths use relative paths (not Windows-specific like `C:\`)
- Verify data files are in repository:
  ```bash
  git ls-files data/
  ```
- Commit missing files:
  ```bash
  git add data/
  git commit -m "Add data files"
  git push
  ```

#### **3. "GDAL not found" or Geospatial Errors**
**Cause:** System dependencies not installed
**Solution:**
- Verify `packages.txt` is in repository root
- Check Streamlit Cloud logs for apt-get errors
- Restart deployment if needed

#### **4. Memory Issues**
**Cause:** Large data files or insufficient memory
**Solution:**
- Streamlit Community Cloud has 1 GB RAM limit (free tier)
- Consider optimizing data loading with caching
- Use `@st.cache_data` decorators (already implemented)

#### **5. Slow Performance**
**Cause:** Cold start or large data processing
**Solution:**
- First load is always slower (cold start)
- Subsequent loads use cache (faster)
- Consider optimizing heavy computations

---

## 🎯 Post-Deployment

### **Testing Checklist**

After deployment, verify all features work:

- [ ] **Home page loads** with map and statistics
- [ ] **Navigation** between all 8 pages works
- [ ] **Map interactions** (zoom, pan, layer toggles)
- [ ] **Data analysis** pages load correctly
- [ ] **Raster analysis** with MapBiomas data
- [ ] **Proximity analysis** functionality
- [ ] **Export features** work
- [ ] **Accessibility features** (keyboard navigation, screen readers)

### **Performance Monitoring**

Monitor application health:
1. Check Streamlit Cloud dashboard for:
   - Uptime status
   - Resource usage (CPU, memory)
   - Error logs
   - User analytics

2. Set up monitoring alerts:
   - Downtime notifications
   - Error rate alerts

### **Updating the Application**

To deploy updates:
```bash
# Make changes locally
git add .
git commit -m "Description of changes"
git push origin main

# Streamlit Cloud auto-deploys on push to main branch
```

### **Rollback Strategy**

If deployment fails:
1. Check deployment logs in Streamlit Cloud
2. Fix issues locally
3. Push fix to GitHub
4. Or rollback to previous version:
   ```bash
   git revert HEAD
   git push origin main
   ```

---

## 🌐 Accessing Your Application

### **Production URL**
After successful deployment, your app will be available at:
```
https://[your-chosen-name].streamlit.app
```

### **Custom Domain (Optional)**
Streamlit Cloud supports custom domains:
1. Go to app settings
2. Add your custom domain
3. Configure DNS settings

---

## 📊 Resource Limits (Streamlit Community Cloud)

### **Free Tier Limits:**
- **RAM:** 1 GB
- **CPU:** 1 vCPU shared
- **Storage:** Limited by GitHub repository size
- **Bandwidth:** Unlimited viewers
- **Uptime:** Apps sleep after inactivity (wake on visit)

### **If You Need More:**
- Consider Streamlit Cloud Teams plan
- Or deploy to alternative platforms (AWS, GCP, Azure)

---

## 🔐 Security Considerations

### **Already Implemented:**
- ✅ XSRF protection enabled
- ✅ Secrets not in version control (`.gitignore`)
- ✅ CORS disabled
- ✅ Secure headers in configuration

### **Best Practices:**
- Keep dependencies updated
- Monitor for security vulnerabilities
- Use secrets management for sensitive data
- Implement rate limiting if needed

---

## 📞 Support & Resources

### **Streamlit Resources:**
- [Streamlit Documentation](https://docs.streamlit.io)
- [Streamlit Community Forum](https://discuss.streamlit.io)
- [Streamlit Cloud Status](https://status.streamlit.io)

### **Project Resources:**
- **GitHub Repository:** [https://github.com/aikiesan/cp2b_maps_v2](https://github.com/aikiesan/cp2b_maps_v2)
- **Issues:** Report bugs on GitHub Issues
- **Documentation:** See project README.md

---

## ✅ Deployment Success Checklist

- [ ] All files pushed to GitHub
- [ ] Application deployed on Streamlit Cloud
- [ ] All pages load correctly
- [ ] Data files accessible
- [ ] Map visualizations working
- [ ] Performance acceptable
- [ ] Accessibility features functional
- [ ] URL shared with users

---

**🎉 Congratulations! CP2B Maps V2 is now live in production!**

*For UI/UX improvements and future enhancements, see `NEXT_PHASE_DEVELOPMENT_GUIDE.md`*