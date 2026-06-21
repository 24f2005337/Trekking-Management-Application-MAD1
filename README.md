# 🏔️ TrekPro Portal — Full-Stack Trekking Management Application

Adventure organizations require efficient systems to manage trekking activities involving trek organizers, staff, and participants. Currently, many trekking groups rely on spreadsheets, phone calls, or manual coordination, which makes it difficult to manage trek approvals, track bookings, avoid overbooking, and maintain trek history.

You are required to build a Trekking Management Application web application that allows Admin, Trek Staff, and Users (Trekkers) to interact with the system based on their roles.

The application focuses on a multi-role authorization framework, strict data integrity constraints, live capacity allocation trackers, and complex dynamic views, all delivered via a pure server-side architecture without relying on any JavaScript framework.

---

## 🛠️ Tech Stack & Structural Architecture

The project is split following the industry-standard clean **Model-View-Controller (MVC) Architectural Pattern** to keep the business logic, database blueprints, and UI views completely segregated:

* **Backend Engine:** Python 3.x with Flask Framework
* **Data Layer (ORM):** Flask-SQLAlchemy (Object-Relational Mapping system)
* **Storage Engine:** SQLite 3 (Lightweight relational file database)
* **Frontend Matrix:** Semantic HTML5, CSS3, Jinja2 Templating Engine, and Bootstrap 5.3 UI Components framework.

---

## 📁 Project Directory Tree Layout

TREKKING MANAGEMENT APPLICATION/
├── applications/
│   ├── controllers.py       # Core endpoints, CRUD matrix operations & multi-filters
│   ├── database.py          # Relational database pipeline initializer setup
│   └── models.py            # Database blueprints (User, StaffProfile, Trek, Booking)
├── instance/
│   └── trekking.db          # Pre-seeded test databases with live records
├── templates/
│   ├── admin_dashboard.html # Superuser hub (Forms, search anchors, global registries)
│   ├── base.html            # Core scaffolding structure (Navbar, layout sheets, footer)
│   ├── edit_trek.html       # Dynamic specifications modifier configuration window
│   ├── index.html           # Brand marketing landing screen entrypoint
│   ├── login.html           # Secure sessions authorization validation portal
│   ├── register.html        # New Trekker client onboarding gateway
│   ├── staff_dashboard.html # Guide portfolio manager & state lifecycle controllers
│   ├── trek_participants.html # Manifest verification view for crew operations
│   └── trekker_dashboard.html # Asset mapped consumer itinerary booking dashboard
└── app.py                   # Core runtime application orchestrator startup file



## 🔒 Security Design & Architectural Integrity

1. **Role Enforcement Guards:** Every individual system endpoint is secured with an explicit authorization block. If a user attempts to access `/admin/dashboard` by manually tampering with the URL, the backend validation interceptor immediately halts execution and returns a `403 Unauthorized` status code.

2. **Access Control Kill-Switch (Blacklist Engine):** The Administrator can take immediate action to blacklist any abusive user or spam profile from the registration table. The moment a profile is blacklisted, the backend dynamically clears their active session tokens and completely blocks all future login parameters.

3. **Inventory Overflow Counter Guards:** To manage race conditions and inventory control, strict database constraints check and verify that a ticket/booking is processed only if `available_slots > 0`. The exact moment a trek is filled, the portal action updates automatically to render a "Sold Out" state on the client layout.


## 🎨 Advanced Frontend Mechanics (Premium UI without JavaScript)

Adhering strictly to the MAD 1 project requirements, the application delivers fluid user interfaces entirely without client-side scripts (JavaScript) by leveraging pure server-side state mechanisms:

1. **Dynamic Content Asset Mapping:** The client-side dashboard implements conditional Jinja2 loops that scan destination location tags (e.g., Himachal, Uttarakhand) to mathematically map and dynamically fetch corresponding static image placeholders (via picsum.photos IDs).

2. **Auto-Focus Anchor Jumps:** To eliminate tedious page re-scrolling when data search queries are executed on the long administrative master page, HTML anchor IDs (`#treks-section`, `#users-section`) are utilized. The backend controllers append these fragment identifiers to redirect URLs, instantly focusing the user's viewport on the intended data section.
