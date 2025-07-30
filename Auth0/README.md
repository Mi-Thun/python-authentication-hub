
# Auth0 Setup Guide

## 1. Access Auth0 Dashboard
Go to: [Auth0 Dashboard](https://manage.auth0.com/dashboard/)

---

## 2. Create Application
1. Click **Applications** > **Create Application**
2. Name: `Default App`
3. Choose type as needed (e.g., Regular Web Application)

---

## 3. Create API
1. Go to **APIs** > **Create API**
2. Name: `System API`
3. Identifier: `https://myapi.myapp.com`
4. JWT Profile: `RFC 9068`
5. Signing Algorithm: `RS256`
6. Enable **RBAC**
7. Enable **Add Permissions in Access Token**

---

## 4. Add API Permissions
1. In your API, go to **Permissions**
2. Add permission: `read:messages`

---

## 5. Authorize Machine to Machine Applications
1. In your API, go to **Machine to Machine Applications**
2. Authorize your application (toggle **Authorized** ON)

---

## 6. Application Settings
1. Go to your application (**Default App**) > **Settings**
2. Set:
   - **Allowed Callback URLs**: `http://localhost:7000/callback`
   - **Allowed Logout URLs**: `http://localhost:7000`
   - **Allowed Web Origins**: `http://localhost:7000`
   - **Set Maximum Refresh Token Lifetime**: ON
   - **Allow Refresh Token Rotation**: ON

---

## 7. Add Custom Action for Roles
1. Go to **Actions** > **Library**
2. Click **Create Action** > **Build from Scratch**
   - Name: `Add Role to Login`
   - Trigger: `Login / Post Login`
   - Runtime: `Node 22`
3. Add the following code:
   ```js
   exports.onExecutePostLogin = async (event, api) => {
     const namespace = 'https://myapp.example.com/';
     if (event.user) {
       const assignedRoles = (event.authorization && event.authorization.roles) || [];
       api.idToken.setCustomClaim(`${namespace}roles`, assignedRoles);
       api.accessToken.setCustomClaim(`${namespace}roles`, assignedRoles);
     }
   };
   ```
4. Click **Deploy**

---

## 8. Enable Action Trigger
1. Go to **Actions** > **Flows**
2. In **Post Login** flow, drag and drop `Add Role to Login` action

---

**Your Auth0 setup is now complete!**


