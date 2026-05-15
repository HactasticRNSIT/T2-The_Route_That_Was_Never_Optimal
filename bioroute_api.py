from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import textwrap

W, H = A4

doc = SimpleDocTemplate(
    "/mnt/user-data/outputs/BioRoute_MVP_API_Contract.pdf",
    pagesize=A4,
    leftMargin=1.8*cm, rightMargin=1.8*cm,
    topMargin=2*cm, bottomMargin=2*cm
)

# ── Colours ──────────────────────────────────────────────
DARK_BG   = colors.HexColor("#0F1923")
GREEN_ACC = colors.HexColor("#22C55E")
BLUE_ACC  = colors.HexColor("#3B82F6")
ORANGE    = colors.HexColor("#F97316")
RED_ACC   = colors.HexColor("#EF4444")
YELLOW    = colors.HexColor("#EAB308")
MUTED_BG  = colors.HexColor("#1E2D3D")
CODE_BG   = colors.HexColor("#111827")
TEXT_MAIN = colors.HexColor("#E2E8F0")
TEXT_DIM  = colors.HexColor("#94A3B8")
TEAL      = colors.HexColor("#14B8A6")
WHITE     = colors.white

styles = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

cover_title = S("CoverTitle",
    fontSize=34, textColor=WHITE, leading=42,
    fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=8)

cover_sub = S("CoverSub",
    fontSize=15, textColor=GREEN_ACC, leading=20,
    fontName="Helvetica", alignment=TA_CENTER, spaceAfter=6)

cover_tag = S("CoverTag",
    fontSize=11, textColor=TEXT_DIM, leading=16,
    fontName="Helvetica", alignment=TA_CENTER, spaceAfter=4)

h1 = S("H1",
    fontSize=20, textColor=GREEN_ACC, fontName="Helvetica-Bold",
    spaceBefore=18, spaceAfter=6, leading=26)

h2 = S("H2",
    fontSize=14, textColor=BLUE_ACC, fontName="Helvetica-Bold",
    spaceBefore=14, spaceAfter=4, leading=18)

h3 = S("H3",
    fontSize=11, textColor=ORANGE, fontName="Helvetica-Bold",
    spaceBefore=10, spaceAfter=3, leading=15)

body = S("Body",
    fontSize=9, textColor=TEXT_MAIN, fontName="Helvetica",
    spaceBefore=3, spaceAfter=3, leading=14)

body_dim = S("BodyDim",
    fontSize=8.5, textColor=TEXT_DIM, fontName="Helvetica",
    spaceBefore=2, spaceAfter=2, leading=13)

code = S("Code",
    fontSize=7.8, textColor=GREEN_ACC, fontName="Courier",
    spaceBefore=2, spaceAfter=2, leading=12,
    backColor=CODE_BG, leftIndent=8, rightIndent=8,
    borderPadding=(4,4,4,4))

code_w = S("CodeW",
    fontSize=7.8, textColor=TEXT_MAIN, fontName="Courier",
    spaceBefore=0, spaceAfter=0, leading=12)

code_key = S("CodeKey",
    fontSize=7.8, textColor=YELLOW, fontName="Courier-Bold",
    spaceBefore=0, spaceAfter=0, leading=12)

badge_red = S("BadgeRed",
    fontSize=8, textColor=WHITE, fontName="Helvetica-Bold",
    backColor=RED_ACC, borderPadding=(2,6,2,6))

badge_green = S("BadgeGreen",
    fontSize=8, textColor=WHITE, fontName="Helvetica-Bold",
    backColor=colors.HexColor("#15803D"), borderPadding=(2,6,2,6))

badge_blue = S("BadgeBlue",
    fontSize=8, textColor=WHITE, fontName="Helvetica-Bold",
    backColor=colors.HexColor("#1D4ED8"), borderPadding=(2,6,2,6))

note_style = S("Note",
    fontSize=8.5, textColor=TEXT_DIM, fontName="Helvetica-Oblique",
    spaceBefore=2, spaceAfter=6, leading=13, leftIndent=10)

def hr(): return HRFlowable(width="100%", thickness=0.5, color=MUTED_BG, spaceAfter=6, spaceBefore=6)
def gap(n=6): return Spacer(1, n)
def P(txt, st=None): return Paragraph(txt, st or body)
def pb(): return PageBreak()

def section_header(text):
    return [
        gap(4),
        Table([[Paragraph(text, S("SH", fontSize=18, textColor=WHITE,
                fontName="Helvetica-Bold", leading=24))]],
              colWidths=[doc.width],
              style=TableStyle([
                  ("BACKGROUND", (0,0), (-1,-1), DARK_BG),
                  ("TOPPADDING",(0,0),(-1,-1),10),
                  ("BOTTOMPADDING",(0,0),(-1,-1),10),
                  ("LEFTPADDING",(0,0),(-1,-1),12),
              ])),
        gap(8),
    ]

def method_badge(method):
    colors_map = {"GET": "#15803D","POST":"#1D4ED8","PATCH":"#B45309","DELETE":"#991B1B"}
    c = colors_map.get(method, "#374151")
    return Paragraph(f'<font color="white"><b>{method}</b></font>',
        S(f"MB{method}", fontSize=9, fontName="Helvetica-Bold",
          backColor=colors.HexColor(c), borderPadding=(3,8,3,8),
          textColor=WHITE))

def endpoint_header(method, url, title):
    mbox = method_badge(method)
    url_p = Paragraph(f'<font color="#94A3B8">{url}</font>',
        S("URL", fontSize=10, fontName="Courier-Bold", leading=14, textColor=TEXT_DIM))
    title_p = Paragraph(title, S("EPTitle", fontSize=11, fontName="Helvetica-Bold",
        textColor=WHITE, leading=14))
    t = Table(
        [[mbox, url_p]],
        colWidths=[60, doc.width-60],
        style=TableStyle([
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LEFTPADDING",(0,0),(-1,-1),0),
            ("RIGHTPADDING",(0,0),(-1,-1),4),
        ])
    )
    return [
        gap(10),
        Table([[title_p]], colWidths=[doc.width],
              style=TableStyle([("LEFTPADDING",(0,0),(-1,-1),0)])),
        t,
        gap(4),
    ]

def label(txt, col=None):
    c = col or TEAL
    return Paragraph(f'<font color="#{c.hexval()[2:] if hasattr(c,"hexval") else "14B8A6"}"><b>{txt}</b></font>',
        S("LBL", fontSize=8.5, fontName="Helvetica-Bold", textColor=c, spaceBefore=6, spaceAfter=2))

def code_block(lines):
    items = []
    rows = []
    for line in lines.split('\n'):
        rows.append([Paragraph(line, code_w)])
    t = Table(rows, colWidths=[doc.width],
              style=TableStyle([
                  ("BACKGROUND",(0,0),(-1,-1), CODE_BG),
                  ("TOPPADDING",(0,0),(-1,-1),1),
                  ("BOTTOMPADDING",(0,0),(-1,-1),1),
                  ("LEFTPADDING",(0,0),(-1,-1),10),
                  ("RIGHTPADDING",(0,0),(-1,-1),6),
              ]))
    return t

def two_col_note(left_label, left_text, right_label, right_text):
    lp = [Paragraph(f"<b><font color='#F97316'>{left_label}</font></b>", body),
          Paragraph(left_text, body_dim)]
    rp = [Paragraph(f"<b><font color='#3B82F6'>{right_label}</font></b>", body),
          Paragraph(right_text, body_dim)]
    hw = doc.width / 2 - 4
    t = Table([[lp, rp]], colWidths=[hw, hw],
              style=TableStyle([
                  ("VALIGN",(0,0),(-1,-1),"TOP"),
                  ("LEFTPADDING",(0,0),(-1,-1),0),
                  ("RIGHTPADDING",(0,0),(-1,-1),8),
              ]))
    return t

def endpoint_table(rows):
    header = ["#","Method","Endpoint","Purpose"]
    data = [header] + rows
    col_w = [22, 48, 190, doc.width-22-48-190]
    ts = TableStyle([
        ("BACKGROUND",(0,0),(-1,0), DARK_BG),
        ("TEXTCOLOR",(0,0),(-1,0), GREEN_ACC),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1), 8),
        ("FONTNAME",(0,1),(-1,-1),"Helvetica"),
        ("TEXTCOLOR",(0,1),(-1,-1), TEXT_MAIN),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[CODE_BG, MUTED_BG]),
        ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#1E2D3D")),
        ("TOPPADDING",(0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),6),
        ("RIGHTPADDING",(0,0),(-1,-1),6),
        ("TEXTCOLOR",(1,1),(1,-1), BLUE_ACC),
        ("FONTNAME",(1,1),(1,-1),"Courier-Bold"),
        ("TEXTCOLOR",(2,1),(2,-1), colors.HexColor("#A78BFA")),
        ("FONTNAME",(2,1),(2,-1),"Courier"),
    ])
    t = Table(data, colWidths=col_w, style=ts)
    return t

def schema_table(rows, title=""):
    header = ["Field","Type","Notes"]
    data = [header] + rows
    col_w = [130, 100, doc.width-230]
    ts = TableStyle([
        ("BACKGROUND",(0,0),(-1,0), DARK_BG),
        ("TEXTCOLOR",(0,0),(-1,0), TEAL),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1), 8),
        ("FONTNAME",(0,1),(-1,-1),"Helvetica"),
        ("TEXTCOLOR",(0,1),(-1,-1), TEXT_MAIN),
        ("TEXTCOLOR",(1,1),(1,-1), YELLOW),
        ("FONTNAME",(0,1),(0,-1),"Courier"),
        ("FONTNAME",(1,1),(1,-1),"Courier"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[CODE_BG, MUTED_BG]),
        ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#1E2D3D")),
        ("TOPPADDING",(0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),6),
        ("RIGHTPADDING",(0,0),(-1,-1),6),
    ])
    return Table(data, colWidths=col_w, style=ts)

# ═══════════════════════════════════════════════════════
# BUILD DOCUMENT
# ═══════════════════════════════════════════════════════
story = []

# ── COVER ────────────────────────────────────────────────
story += [
    gap(60),
    Table([[
        Paragraph("🧫", S("Emoji", fontSize=52, alignment=TA_CENTER, leading=64))
    ]], colWidths=[doc.width],
         style=TableStyle([("ALIGN",(0,0),(0,0),"CENTER")])),
    gap(16),
    Paragraph("BioRoute", cover_title),
    Paragraph("Slime Mold Garbage Collection Optimizer", cover_sub),
    gap(12),
    Paragraph("Hackathon MVP — Complete API Contract", cover_tag),
    Paragraph("Node.js · Express · React · Leaflet.js · Supabase · Firebase", cover_tag),
    gap(30),
]

# Stack badges
badges = [
    ("19 Endpoints","#15803D"), ("PostGIS Geospatial","#1D4ED8"),
    ("Firebase Realtime","#B45309"), ("YOLOv8 Vision","#7C3AED"),
    ("Slime Mold VRP","#0F766E"), ("Bangalore Routing","#991B1B"),
]
badge_data = [[Paragraph(f'<font color="white"><b>{t}</b></font>',
    S(f"B{i}", fontSize=8.5, fontName="Helvetica-Bold", backColor=colors.HexColor(c),
      borderPadding=(4,10,4,10), textColor=WHITE))
    for t,c in badges]]
story.append(Table(badge_data, colWidths=[doc.width/6]*6,
    style=TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),
                      ("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3)])))

story += [gap(40), pb()]

# ── SECTION 1: OVERVIEW ───────────────────────────────────
story += section_header("1 · MVP API Overview")
story += [
    P("BioRoute is a smart waste management platform for Bangalore. This document covers all 19 hackathon MVP endpoints, compact data models, priority scoring, slime mold route optimization logic, and frontend integration guidance.", body),
    gap(8),
]

overview_rows = [
    ["Demo Flow","Description"],
    ["Step 1","Citizen submits geotagged waste report with optional photo"],
    ["Step 2","Admin verifies or rejects the report"],
    ["Step 3","System calculates hotspot priority score (formula-driven)"],
    ["Step 4","System generates optimized truck route via slime mold logic"],
    ["Step 5","Dashboard compares static vs optimized route (savings shown)"],
    ["Step 6","Simulated truck moves on map using Firebase realtime coords"],
]
ts = TableStyle([
    ("BACKGROUND",(0,0),(-1,0), DARK_BG), ("TEXTCOLOR",(0,0),(-1,0), GREEN_ACC),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"), ("FONTNAME",(0,1),(-1,-1),"Helvetica"),
    ("FONTSIZE",(0,0),(-1,-1),8.5), ("TEXTCOLOR",(0,1),(-1,-1),TEXT_MAIN),
    ("TEXTCOLOR",(0,1),(0,-1), YELLOW), ("FONTNAME",(0,1),(0,-1),"Helvetica-Bold"),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[CODE_BG, MUTED_BG]),
    ("GRID",(0,0),(-1,-1),0.3,MUTED_BG),
    ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("LEFTPADDING",(0,0),(-1,-1),8),
])
story.append(Table(overview_rows, colWidths=[80, doc.width-80], style=ts))
story.append(gap(10))

# ── SECTION 2: TECH STACK ─────────────────────────────────
story += section_header("2 · Recommended Tech Stack (JavaScript)")

stack = [
    ["Layer","Technology","Package / Notes"],
    ["Frontend","React 18 + Tailwind CSS","Zustand for state, React-Query for data fetching"],
    ["Map","Leaflet.js + react-leaflet","GeoJSON LineString for route polylines"],
    ["Backend","Node.js 20 LTS + Express 5","REST API, Multer for uploads, node-cron for scheduler"],
    ["Primary DB","Supabase PostgreSQL + PostGIS","Geography(Point,4326) for all location fields"],
    ["Realtime","Firebase Realtime Database","Live truck coords only — NOT the main DB"],
    ["Storage","Supabase Storage","Citizen photos, bin camera images"],
    ["Auth","jsonwebtoken + bcrypt","JWT 24h access, 7d refresh tokens"],
    ["Routing API","OpenRouteService (free)","Route polyline + distance matrix"],
    ["Image AI","Roboflow Inference API","YOLOv8 bin overflow detection"],
    ["NLP","Custom keyword extractor","Regex + OpenAI GPT-4o-mini fallback"],
    ["Validation","zod","Schema validation on all request bodies"],
    ["Rate Limit","express-rate-limit","10 req/min on public citizen endpoints"],
    ["Env Config","dotenv","All secrets in .env — never commit"],
]
ts2 = TableStyle([
    ("BACKGROUND",(0,0),(-1,0),DARK_BG),("TEXTCOLOR",(0,0),(-1,0),TEAL),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),
    ("TEXTCOLOR",(0,1),(-1,-1),TEXT_MAIN),("TEXTCOLOR",(0,1),(0,-1),YELLOW),
    ("FONTNAME",(0,1),(0,-1),"Helvetica-Bold"),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[CODE_BG,MUTED_BG]),
    ("GRID",(0,0),(-1,-1),0.3,MUTED_BG),
    ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
    ("LEFTPADDING",(0,0),(-1,-1),6),
])
story.append(Table(stack, colWidths=[90,160,doc.width-250], style=ts2))
story += [gap(8), pb()]

# ── SECTION 3: DATABASE ARCHITECTURE ─────────────────────
story += section_header("3 · Database & Location Architecture")
story += [
    P("<b>Rule:</b> Supabase PostgreSQL + PostGIS for everything relational. Firebase ONLY for live truck coordinates.", body),
    gap(6),
]

db_split = [
    ["Supabase PostgreSQL + PostGIS","Firebase Realtime Database","Supabase Storage"],
    ["waste_points, citizen_reports,\nhotspots, trucks, depots,\nroutes, route_stops,\npriority_scores, analytics",
     "currentLatitude\ncurrentLongitude\ncurrentSpeed\ncurrentHeading\nrouteProgressPercent\ncurrentStopIndex",
     "citizen_photos/\nbin_camera_images/\ndetection_snapshots/"],
]
ts3 = TableStyle([
    ("BACKGROUND",(0,0),(-1,0),DARK_BG),("TEXTCOLOR",(0,0),(-1,0),GREEN_ACC),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),
    ("TEXTCOLOR",(0,1),(-1,-1),TEXT_MAIN),("FONTNAME",(0,1),(-1,-1),"Courier"),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[CODE_BG]),
    ("GRID",(0,0),(-1,-1),0.5,MUTED_BG),
    ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
    ("LEFTPADDING",(0,0),(-1,-1),8),("VALIGN",(0,0),(-1,-1),"TOP"),
])
story.append(Table(db_split, colWidths=[doc.width/3]*3, style=ts3))
story += [gap(10),
    P("<b>PostGIS field convention:</b>", h3),
    code_block(
        "-- Every location-aware table gets this column:\n"
        "location  geography(Point, 4326)   -- SRID 4326 = WGS84 (GPS)\n\n"
        "-- Geospatial queries used:\n"
        "ST_DWithin(location, ST_MakePoint(lng,lat)::geography, radius_meters)\n"
        "ST_Distance(a.location, b.location)\n"
        "ST_AsGeoJSON(location)"
    ),
    gap(10), pb(),
]

# ── SECTION 4: COMMON RESPONSE FORMAT ─────────────────────
story += section_header("4 · Common Response Format")
story += [
    P("<b>All API responses follow this envelope:</b>", body), gap(4),
    code_block(
        '// SUCCESS\n'
        '{\n'
        '  "success": true,\n'
        '  "message": "Request completed successfully",\n'
        '  "data": { ... },\n'
        '  "meta": {\n'
        '    "requestId": "req_9f2a3b",\n'
        '    "timestamp": "2026-05-08T18:30:00+05:30"\n'
        '  }\n'
        '}'
    ),
    gap(8),
    code_block(
        '// ERROR\n'
        '{\n'
        '  "success": false,\n'
        '  "error": {\n'
        '    "code": "VALIDATION_ERROR",\n'
        '    "message": "Invalid latitude value — must be between -90 and 90",\n'
        '    "details": [\n'
        '      { "field": "latitude", "message": "Expected number -90..90" }\n'
        '    ]\n'
        '  },\n'
        '  "meta": { "requestId": "req_9f2a3b", "timestamp": "2026-05-08T18:30:00+05:30" }\n'
        '}'
    ),
    gap(8),
]

error_codes = [
    ["Code","HTTP","Meaning"],
    ["VALIDATION_ERROR","400","Bad request body / params"],
    ["UNAUTHORIZED","401","Missing or invalid JWT"],
    ["FORBIDDEN","403","Role not permitted for this action"],
    ["NOT_FOUND","404","Resource does not exist"],
    ["RATE_LIMITED","429","Too many requests (citizen endpoints: 10/min)"],
    ["OPTIMIZATION_FAILED","422","Slime mold route optimizer error"],
    ["DETECTION_FAILED","422","YOLOv8 inference error"],
    ["INTERNAL_ERROR","500","Unexpected server error"],
]
ts4 = TableStyle([
    ("BACKGROUND",(0,0),(-1,0),DARK_BG),("TEXTCOLOR",(0,0),(-1,0),TEAL),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),
    ("TEXTCOLOR",(0,1),(0,-1),YELLOW),("FONTNAME",(0,1),(0,-1),"Courier-Bold"),
    ("TEXTCOLOR",(1,1),(1,-1),RED_ACC),("FONTNAME",(1,1),(1,-1),"Courier-Bold"),
    ("TEXTCOLOR",(2,1),(2,-1),TEXT_MAIN),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[CODE_BG,MUTED_BG]),
    ("GRID",(0,0),(-1,-1),0.3,MUTED_BG),
    ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
    ("LEFTPADDING",(0,0),(-1,-1),8),
])
story.append(Table(error_codes, colWidths=[140,50,doc.width-190], style=ts4))
story += [gap(8), pb()]

# ── SECTION 5: DATA MODELS ────────────────────────────────
story += section_header("5 · Compact Data Models")

models = {
    "Truck": [
        ["truckId","VARCHAR PK","truck_001"],
        ["vehicleNumber","VARCHAR","KA01AB1234"],
        ["capacityKg","INTEGER","3000"],
        ["currentLoadKg","INTEGER","0"],
        ["status","ENUM","available | assigned | active | maintenance"],
        ["assignedRouteId","VARCHAR FK","route_001 or null"],
        ["fuelEfficiencyKmL","FLOAT","5.2"],
        ["location","geography(Point,4326)","PostGIS live location"],
        ["lastUpdatedAt","TIMESTAMPTZ","ISO 8601"],
    ],
    "Depot": [
        ["depotId","VARCHAR PK","depot_ejipura"],
        ["name","VARCHAR","Ejipura Depot"],
        ["address","TEXT","8th Cross, Ejipura, Bengaluru"],
        ["location","geography(Point,4326)","PostGIS point"],
        ["latitude","FLOAT","12.9510"],
        ["longitude","FLOAT","77.6245"],
        ["capacityTrucks","INTEGER","10"],
        ["activeTruckCount","INTEGER","3"],
    ],
    "WastePoint": [
        ["wastePointId","VARCHAR PK","wp_001"],
        ["name","VARCHAR","Near Apollo Clinic Bin"],
        ["location","geography(Point,4326)","PostGIS point"],
        ["latitude","FLOAT","12.9784"],
        ["longitude","FLOAT","77.6408"],
        ["address","TEXT","100 Feet Rd, Indiranagar"],
        ["area","VARCHAR","Indiranagar"],
        ["fillLevelPercent","INTEGER","0–100"],
        ["wasteType","ENUM","hospital_biomedical | chemical_industrial | organic_black_spot | regular_waste | plastic_dry | e_waste | large_debris | mixed_waste"],
        ["toxicityLevel","ENUM","low | moderate | high | critical"],
        ["populationDensity","ENUM","low | medium | high | very_high"],
        ["roadType","ENUM","narrow_lane | residential_road | arterial_road | market_road | industrial_road"],
        ["estimatedWasteKg","FLOAT","Weight estimate"],
        ["priorityScore","FLOAT","Calculated score"],
        ["priorityLevel","ENUM","low | normal | high | critical"],
        ["lastCollectedAt","TIMESTAMPTZ","ISO 8601"],
        ["status","ENUM","active | collected | inactive"],
    ],
    "CitizenReport": [
        ["reportId","VARCHAR PK","rep_001"],
        ["citizenName","VARCHAR","Optional"],
        ["mobileNumber","VARCHAR","Stored hashed"],
        ["location","geography(Point,4326)","PostGIS point"],
        ["latitude","FLOAT","12.9352"],
        ["longitude","FLOAT","77.6245"],
        ["address","TEXT","Residency Rd, Koramangala"],
        ["landmark","VARCHAR","Near More Supermarket"],
        ["area","VARCHAR","Koramangala"],
        ["geotagSource","ENUM","browser_geolocation | manual_pin | typed_address"],
        ["geotagAccuracyMeters","FLOAT","GPS accuracy"],
        ["wasteCategory","ENUM","see wasteType above"],
        ["severity","ENUM","low | medium | high | critical"],
        ["description","TEXT","Citizen free text"],
        ["photoUrl","TEXT","Supabase Storage URL"],
        ["verificationStatus","ENUM","pending | verified | rejected"],
        ["generatedHotspotId","VARCHAR FK","hotspot_001 or null"],
        ["createdAt","TIMESTAMPTZ","ISO 8601"],
    ],
    "Hotspot": [
        ["hotspotId","VARCHAR PK","hotspot_001"],
        ["sourceType","ENUM","image_detection | citizen_report | text_complaint | manual_admin"],
        ["sourceId","VARCHAR FK","ID of source record"],
        ["location","geography(Point,4326)","PostGIS point"],
        ["latitude","FLOAT","12.9784"],
        ["longitude","FLOAT","77.6408"],
        ["address","TEXT","Full address"],
        ["area","VARCHAR","Indiranagar"],
        ["wasteType","ENUM","see wasteType enum"],
        ["fillLevelPercent","INTEGER","0–100"],
        ["estimatedWasteKg","FLOAT","Weight estimate"],
        ["toxicityLevel","ENUM","low | moderate | high | critical"],
        ["populationDensity","ENUM","low | medium | high | very_high"],
        ["roadType","ENUM","see roadType enum"],
        ["priorityScore","FLOAT","Final calculated score"],
        ["priorityLevel","ENUM","low | normal | high | critical"],
        ["status","ENUM","active | verified | assigned_to_route | collected | rejected"],
        ["createdAt","TIMESTAMPTZ","ISO 8601"],
        ["verifiedAt","TIMESTAMPTZ","When admin verified"],
    ],
    "PriorityScore": [
        ["priorityScoreId","VARCHAR PK","ps_001"],
        ["hotspotId","VARCHAR FK","hotspot_001"],
        ["baseWasteTypeScore","FLOAT","e.g. 100 for hospital_biomedical"],
        ["timeOverflowPenalty","FLOAT","+5 per 6hr after 80% fill"],
        ["populationDensityBoost","FLOAT","0 | 8 | 15 | 20"],
        ["citizenSeverityBoost","FLOAT","5 | 10 | 20 | 30"],
        ["toxicityBoost","FLOAT","0 | 5 | 10 | 20"],
        ["finalPriorityScore","FLOAT","Sum of all components"],
        ["priorityLevel","ENUM","low | normal | high | critical"],
        ["explanation","TEXT","Human-readable breakdown"],
        ["calculatedAt","TIMESTAMPTZ","ISO 8601"],
    ],
    "Route": [
        ["routeId","VARCHAR PK","route_001"],
        ["jobId","VARCHAR FK","opt_job_001"],
        ["routeType","ENUM","static | optimized | citizen_inclusive"],
        ["assignedTruckId","VARCHAR FK","truck_001"],
        ["assignedDriverId","VARCHAR FK","driver_001"],
        ["depotStartId","VARCHAR FK","depot_ejipura"],
        ["depotEndId","VARCHAR FK","depot_ejipura"],
        ["routeDate","DATE","2026-05-09"],
        ["totalDistanceKm","FLOAT","28.4"],
        ["estimatedDurationMin","FLOAT","195"],
        ["estimatedFuelLiters","FLOAT","5.46"],
        ["estimatedCO2Kg","FLOAT","14.6"],
        ["totalWasteKg","FLOAT","1840"],
        ["totalStops","INTEGER","12"],
        ["routePolylineGeoJson","JSONB","GeoJSON LineString"],
        ["status","ENUM","planned | approved | dispatched | active | completed | cancelled"],
        ["createdAt","TIMESTAMPTZ","ISO 8601"],
    ],
    "RouteStop": [
        ["stopId","VARCHAR PK","stop_001"],
        ["routeId","VARCHAR FK","route_001"],
        ["sequenceNumber","INTEGER","1-based order"],
        ["sourceType","ENUM","waste_point | hotspot | citizen_report"],
        ["sourceId","VARCHAR","hotspot_001"],
        ["latitude","FLOAT","12.9784"],
        ["longitude","FLOAT","77.6408"],
        ["location","geography(Point,4326)","PostGIS point"],
        ["address","TEXT","Stop address"],
        ["wasteType","ENUM","see wasteType enum"],
        ["priorityScore","FLOAT","Score at time of route generation"],
        ["priorityLevel","ENUM","low | normal | high | critical"],
        ["estimatedPickupKg","FLOAT","120.0"],
        ["eta","TIMESTAMPTZ","2026-05-09T06:15:00+05:30"],
        ["serviceTimeMinutes","FLOAT","8.0"],
        ["status","ENUM","pending | completed | skipped"],
        ["completedAt","TIMESTAMPTZ","null or timestamp"],
    ],
    "RouteOptimizationJob": [
        ["jobId","VARCHAR PK","opt_job_001"],
        ["routeDate","DATE","2026-05-09"],
        ["algorithm","VARCHAR","physarum_slime_mold"],
        ["status","ENUM","queued | running | completed | failed"],
        ["totalHotspotsConsidered","INTEGER","14"],
        ["totalRoutesGenerated","INTEGER","2"],
        ["startedAt","TIMESTAMPTZ","ISO 8601"],
        ["completedAt","TIMESTAMPTZ","ISO 8601"],
        ["errorMessage","TEXT","null if succeeded"],
        ["resultSummary","JSONB","High-level stats"],
    ],
    "AnalyticsSummary": [
        ["analyticsId","VARCHAR PK","analytics_20260509"],
        ["date","DATE","2026-05-09"],
        ["totalHotspots","INTEGER","18"],
        ["criticalHotspots","INTEGER","4"],
        ["totalReports","INTEGER","22"],
        ["totalBinsCollected","INTEGER","14"],
        ["distanceSavedKm","FLOAT","8.3"],
        ["fuelSavedLiters","FLOAT","1.6"],
        ["co2ReducedKg","FLOAT","4.3"],
        ["avgCollectionDelayMin","FLOAT","12.5"],
        ["createdAt","TIMESTAMPTZ","ISO 8601"],
    ],
}

for model_name, fields in models.items():
    story += [
        P(f"<b>{model_name}</b>", h3),
        schema_table(fields),
        gap(8),
    ]

story.append(pb())

# ── SECTION 6: PRIORITY SCORE LOGIC ──────────────────────
story += section_header("6 · Priority Score Logic")
story += [
    P("<b>Formula:</b>", body),
    code_block(
        "priorityScore =\n"
        "  baseWasteTypeScore\n"
        "  + timeOverflowPenalty       // +5 per 6hr after fill >= 80%\n"
        "  + populationDensityBoost    // low:0  medium:8  high:15  very_high:20\n"
        "  + citizenSeverityBoost      // low:5  medium:10  high:20  critical:30\n"
        "  + toxicityBoost             // low:0  moderate:5  high:10  critical:20"
    ),
    gap(6),
]

base_scores = [
    ["Waste Type","Base Score","Priority when fresh"],
    ["hospital_biomedical","100","critical"],
    ["chemical_industrial","85","high"],
    ["e_waste","75","high"],
    ["organic_black_spot","70","high"],
    ["large_debris","55","normal"],
    ["mixed_waste","50","normal"],
    ["plastic_dry","45","normal"],
    ["regular_waste","40","normal"],
]
ts5 = TableStyle([
    ("BACKGROUND",(0,0),(-1,0),DARK_BG),("TEXTCOLOR",(0,0),(-1,0),YELLOW),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8.5),
    ("TEXTCOLOR",(0,1),(0,-1),colors.HexColor("#A78BFA")),("FONTNAME",(0,1),(0,-1),"Courier"),
    ("TEXTCOLOR",(1,1),(1,-1),GREEN_ACC),("FONTNAME",(1,1),(1,-1),"Courier-Bold"),
    ("TEXTCOLOR",(2,1),(2,-1),TEXT_DIM),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[CODE_BG,MUTED_BG]),
    ("GRID",(0,0),(-1,-1),0.3,MUTED_BG),
    ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("LEFTPADDING",(0,0),(-1,-1),8),
])
story.append(Table(base_scores, colWidths=[180,90,doc.width-270], style=ts5))
story += [
    gap(6),
    P("<b>Priority Levels</b> — 0–49 = low | 50–74 = normal | 75–99 = high | 100+ = critical", body_dim),
    gap(6),
    P("<b>Bangalore Monsoon Rule:</b> organic_black_spot nodes get a <b>×3 multiplier</b> during monsoon season (Jun–Sep). Organic decay and smell accelerate significantly — these must be flagged critical automatically.", note_style),
    gap(6),
    P("<b>Segregation Buffer:</b> Poor wet/dry segregation adds 15 min to stop service time (does NOT raise priority score, but affects edge cost).", note_style),
    gap(6),
    P("<b>Example calculation — Indiranagar Biomedical Bin:</b>", body),
    code_block(
        "baseWasteTypeScore      = 100  // hospital_biomedical\n"
        "timeOverflowPenalty     =  15  // 18 hours since overflow (3 × 5)\n"
        "populationDensityBoost  =  15  // high density area\n"
        "citizenSeverityBoost    =  20  // severity = high\n"
        "toxicityBoost           =  20  // toxicity = critical\n"
        "─────────────────────────────\n"
        "finalPriorityScore      = 170  → CRITICAL\n"
        "\n"
        "Marker color on map → RED"
    ),
    gap(8), pb(),
]

# ── SECTION 7: ROUTE OPTIMIZATION LOGIC ──────────────────
story += section_header("7 · Slime Mold Route Optimization Logic")
story += [
    P("The route optimizer is inspired by <b>Physarum polycephalum</b> (slime mold), which finds efficient network paths through reinforcement and pruning.", body),
    gap(6),
    P("<b>Edge Cost Formula:</b>", h3),
    code_block(
        "edgeCost =\n"
        "  baseTravelTimeMinutes       // normalized at 25 km/h truck speed\n"
        "  × trafficMultiplier         // 1.0–2.5 (from ORS / time-of-day estimate)\n"
        "  + uTurnPenalty              // +10 per U-turn\n"
        "  + narrowLanePenalty         // +15 if narrow_lane AND time > 07:30\n"
        "  + carbonDetourPenalty       // +2 per km beyond 2km detour\n"
        "  + roadRestrictionPenalty    // +20 if road type unsuitable for truck\n"
        "\n"
        "nodeServiceTime =\n"
        "  basePickupTime (5 min)\n"
        "  + segregationBuffer         // good:0  moderate:5  poor:15 min\n"
        "  + toxicityHandlingBuffer    // regular:0  organic:5  chemical:10  biomedical:15 min"
    ),
    gap(6),
    P("<b>Bangalore-specific rules hardcoded into optimizer:</b>", h3),
    code_block(
        "// Rule 1 — Narrow lane early-morning constraint\n"
        "if (roadType === 'narrow_lane' && routeStartTime < '07:30') {\n"
        "  narrowLanePenalty = 0;   // collect these first\n"
        "} else if (roadType === 'narrow_lane' && routeStartTime >= '07:30') {\n"
        "  narrowLanePenalty = 15;  // avoid after rush hour\n"
        "}\n"
        "\n"
        "// Rule 2 — Loop route preference\n"
        "// Physarum reinforces edges forming closed circuits.\n"
        "// Open-ended back-and-forth paths get a +20 penalty.\n"
        "\n"
        "// Rule 3 — Truck capacity check\n"
        "if (cumulativeLoadKg + stop.estimatedPickupKg > truck.capacityKg) {\n"
        "  splitToNextTruck();\n"
        "}\n"
        "\n"
        "// Rule 4 — Priority weighting\n"
        "// High-priority nodes act as 'food sources'.\n"
        "// Edge flow from depot to critical nodes is reinforced first.\n"
        "nodeAttractionWeight = priorityScore / 100;"
    ),
    gap(6),
    P("<b>Algorithm steps:</b>", body),
    code_block(
        "1. Load all verified active hotspots as graph nodes\n"
        "2. Build complete edge graph using ORS distance matrix\n"
        "3. Initialize uniform flow across all edges\n"
        "4. Simulate Physarum reinforcement:\n"
        "   — Edges on paths to high-priority nodes gain flow\n"
        "   — Edges with high cost (traffic, U-turns, narrow lanes) lose flow\n"
        "   — Low-flow edges are pruned after N iterations\n"
        "5. Extract strongest-flow edges as the optimized route\n"
        "6. Convert to ordered stop sequence (depot → stops → depot)\n"
        "7. Apply truck capacity check — split if > 3000kg or > 25 stops\n"
        "8. Fetch route polyline GeoJSON from OpenRouteService\n"
        "9. Calculate ETA per stop, fuel estimate, CO2 estimate\n"
        "10. Compare against static baseline route → savings summary"
    ),
    gap(8), pb(),
]

# ── SECTION 8: ENDPOINT SUMMARY TABLE ─────────────────────
story += section_header("8 · Endpoint Summary Table (19 MVP Endpoints)")

ep_rows = [
    ["1","GET","/api/v1/health","Health check — liveness probe"],
    ["2","GET","/api/v1/dashboard/summary","Main dashboard KPI summary"],
    ["3","GET","/api/v1/map/markers","All map markers (bins, hotspots, trucks)"],
    ["4","GET","/api/v1/map/routes","Route polylines (static + optimized GeoJSON)"],
    ["5","GET","/api/v1/waste-points","List all waste points with filters"],
    ["6","POST","/api/v1/waste-points","Create a new waste point / bin"],
    ["7","POST","/api/v1/reports","Submit citizen waste report (public)"],
    ["8","GET","/api/v1/reports","List citizen reports (admin)"],
    ["9","PATCH","/api/v1/reports/:reportId/verify","Admin verifies a citizen report"],
    ["10","PATCH","/api/v1/reports/:reportId/reject","Admin rejects a citizen report"],
    ["11","POST","/api/v1/detections/image","Upload bin image → YOLOv8 detection"],
    ["12","POST","/api/v1/complaints/text","Submit text complaint → NLP extraction"],
    ["13","POST","/api/v1/priority/calculate","Calculate hotspot priority score"],
    ["14","POST","/api/v1/routes/optimize","Trigger slime mold route optimization"],
    ["15","GET","/api/v1/routes/optimization-jobs/:jobId","Poll optimization job status"],
    ["16","GET","/api/v1/routes/tomorrow-plan","Get tomorrow's complete route plan"],
    ["17","GET","/api/v1/trucks","List all trucks with status"],
    ["18","PATCH","/api/v1/trucks/:truckId/location","Update live truck location → Firebase"],
    ["19","GET","/api/v1/analytics/savings","Route savings and carbon analytics"],
]
story.append(endpoint_table(ep_rows))
story += [gap(8),
    P("<b>Auth rules:</b> Endpoints 7, 11, 12 are <b>public</b> (rate-limited 10 req/min). "
      "Endpoints 8,9,10,14,15,16,17,18,19 require <b>admin/supervisor JWT</b>. "
      "Dashboard endpoints (2,3,4) allow admin + driver JWT.", body_dim),
    gap(8), pb(),
]

# ── SECTION 9: DETAILED API CONTRACTS ─────────────────────
story += section_header("9 · Detailed API Contracts")

# Helper to render endpoint
def ep(method, url, title, purpose, auth, query_params, req_body, resp_success, resp_error, fe_note, be_note):
    items = []
    items += endpoint_header(method, url, title)
    items.append(P(f"<b>Purpose:</b> {purpose}", body))
    items.append(P(f"<b>Auth:</b> {auth}", body_dim))
    if query_params:
        items.append(label("Query Parameters", TEAL))
        items.append(code_block(query_params))
    if req_body:
        items.append(label("Request Body", ORANGE))
        items.append(code_block(req_body))
    items.append(label("Success Response 200", GREEN_ACC))
    items.append(code_block(resp_success))
    items.append(label("Error Response", RED_ACC))
    items.append(code_block(resp_error))
    items.append(two_col_note("Frontend Note", fe_note, "Backend Note", be_note))
    items.append(hr())
    return items

# ── EP 1: Health ──────────────────────────────────────────
story += ep(
    "GET", "/api/v1/health", "1 · Health Check",
    "Simple liveness probe. Used by Render/Railway deploy checks and frontend startup.",
    "None — public",
    None, None,
    '{\n  "success": true,\n  "message": "BioRoute API is running",\n'
    '  "data": { "status": "healthy", "uptime": 43200, "version": "1.0.0" },\n'
    '  "meta": { "requestId": "req_h1", "timestamp": "2026-05-08T18:30:00+05:30" }\n}',
    '{ "success": false, "error": { "code": "INTERNAL_ERROR", "message": "Service unavailable" } }',
    "Call on app startup. If not 200, show a maintenance banner.",
    "Express: app.get('/api/v1/health', (req,res) => res.json({...})). No DB call needed."
)

# ── EP 2: Dashboard Summary ───────────────────────────────
story += ep(
    "GET", "/api/v1/dashboard/summary", "2 · Dashboard KPI Summary",
    "Returns all main dashboard stats: hotspot counts, savings, truck status. Powers the top KPI bar.",
    "JWT — admin | supervisor | driver",
    None, None,
    '{\n  "success": true,\n  "data": {\n'
    '    "totalActiveHotspots": 14,\n'
    '    "criticalHotspots": 4,\n'
    '    "verifiedReports": 9,\n'
    '    "pendingReports": 5,\n'
    '    "trucksAvailable": 3,\n'
    '    "routesPlannedTomorrow": 2,\n'
    '    "estimatedDistanceSavedKm": 8.3,\n'
    '    "estimatedFuelSavedLiters": 1.6,\n'
    '    "estimatedCO2ReducedKg": 4.3,\n'
    '    "lastUpdated": "2026-05-08T18:00:00+05:30"\n'
    '  }\n}',
    '{ "success": false, "error": { "code": "UNAUTHORIZED", "message": "Invalid or expired token" } }',
    "Fetch on dashboard mount and refresh every 60s with setInterval. Display in stat cards with Tailwind.",
    "Run 5 COUNT queries on Supabase in parallel with Promise.all(). Cache result for 30s in memory."
)

# ── EP 3: Map Markers ─────────────────────────────────────
story += ep(
    "GET", "/api/v1/map/markers", "3 · Map Markers",
    "Returns all map markers: hotspots, waste points, trucks. Frontend renders them on Leaflet map.",
    "JWT — admin | supervisor | driver",
    "?type=hotspot,waste_point,truck\n?area=Indiranagar\n?priorityLevel=critical,high\n?radiusMeters=5000&lat=12.9716&lng=77.6412",
    None,
    '{\n  "success": true,\n  "data": {\n'
    '    "markers": [\n'
    '      {\n'
    '        "id": "hotspot_001",\n'
    '        "type": "hotspot",\n'
    '        "latitude": 12.9784,\n'
    '        "longitude": 77.6408,\n'
    '        "markerColor": "red",\n'
    '        "priorityLevel": "critical",\n'
    '        "iconType": "hazard",\n'
    '        "popupData": {\n'
    '          "title": "Biomedical Waste Overflow",\n'
    '          "area": "Indiranagar",\n'
    '          "wasteType": "hospital_biomedical",\n'
    '          "fillLevelPercent": 95,\n'
    '          "priorityScore": 170,\n'
    '          "estimatedWasteKg": 180\n'
    '        }\n'
    '      },\n'
    '      {\n'
    '        "id": "truck_001",\n'
    '        "type": "truck",\n'
    '        "latitude": 12.9510,\n'
    '        "longitude": 77.6245,\n'
    '        "markerColor": "blue",\n'
    '        "iconType": "truck",\n'
    '        "popupData": {\n'
    '          "title": "Truck KA01AB1234",\n'
    '          "status": "active",\n'
    '          "currentLoadKg": 840,\n'
    '          "capacityKg": 3000,\n'
    '          "routeProgressPercent": 35\n'
    '        }\n'
    '      }\n'
    '    ],\n'
    '    "total": 2\n'
    '  }\n}',
    '{ "success": false, "error": { "code": "FORBIDDEN", "message": "Access denied" } }',
    "Pass markers array directly to Leaflet. Use markerColor to set L.circleMarker fillColor. "
    "Use popupData to render L.popup HTML. Apply type filter via query param toggles on dashboard.",
    "JOIN hotspots + waste_points + trucks. Apply ST_DWithin for radius filter. "
    "Merge into unified marker format. Truck location comes from Supabase trucks table (not Firebase) for bulk map load."
)

# ── EP 4: Map Routes ──────────────────────────────────────
story += ep(
    "GET", "/api/v1/map/routes", "4 · Map Route Polylines",
    "Returns GeoJSON LineStrings for static and optimized routes. Frontend renders both on map.",
    "JWT — admin | supervisor | driver",
    "?routeDate=2026-05-09\n?routeType=static,optimized",
    None,
    '{\n  "success": true,\n  "data": {\n'
    '    "routes": [\n'
    '      {\n'
    '        "routeId": "route_static_001",\n'
    '        "routeType": "static",\n'
    '        "assignedTruckId": "truck_001",\n'
    '        "color": "#94A3B8",\n'
    '        "lineStyle": "dashed",\n'
    '        "polyline": {\n'
    '          "type": "LineString",\n'
    '          "coordinates": [\n'
    '            [77.6245, 12.9510], [77.6412, 12.9352],\n'
    '            [77.6408, 12.9784], [77.6512, 12.9116]\n'
    '          ]\n'
    '        },\n'
    '        "totalDistanceKm": 36.7,\n'
    '        "estimatedDurationMin": 245\n'
    '      },\n'
    '      {\n'
    '        "routeId": "route_opt_001",\n'
    '        "routeType": "optimized",\n'
    '        "assignedTruckId": "truck_001",\n'
    '        "color": "#3B82F6",\n'
    '        "lineStyle": "solid",\n'
    '        "polyline": {\n'
    '          "type": "LineString",\n'
    '          "coordinates": [\n'
    '            [77.6245, 12.9510], [77.6408, 12.9784],\n'
    '            [77.6412, 12.9352], [77.6512, 12.9116]\n'
    '          ]\n'
    '        },\n'
    '        "totalDistanceKm": 28.4,\n'
    '        "estimatedDurationMin": 195\n'
    '      }\n'
    '    ]\n'
    '  }\n}',
    '{ "success": false, "error": { "code": "NOT_FOUND", "message": "No routes for this date" } }',
    "Use L.geoJSON(polyline) on Leaflet. Set grey dashed style for static, blue solid for optimized. "
    "Toggle visibility with checkbox controls. Color from response 'color' field.",
    "Query routes table by routeDate + routeType. Return stored routePolylineGeoJson JSONB field directly. "
    "If not generated yet, return empty array (frontend shows 'Route not generated yet' state)."
)

story.append(pb())

# ── EP 5: List Waste Points ───────────────────────────────
story += ep(
    "GET", "/api/v1/waste-points", "5 · List Waste Points",
    "Returns all waste points with optional filters. Used for admin bin management and map layer.",
    "JWT — admin | supervisor",
    "?wasteType=hospital_biomedical\n?minFillLevel=80\n?priorityLevel=critical\n?area=Indiranagar\n?status=active\n?limit=50&offset=0",
    None,
    '{\n  "success": true,\n  "data": {\n'
    '    "wastePoints": [\n'
    '      {\n'
    '        "wastePointId": "wp_001",\n'
    '        "name": "Apollo Clinic Bin",\n'
    '        "latitude": 12.9784,\n'
    '        "longitude": 77.6408,\n'
    '        "address": "100 Feet Rd, Indiranagar, Bengaluru",\n'
    '        "area": "Indiranagar",\n'
    '        "fillLevelPercent": 95,\n'
    '        "wasteType": "hospital_biomedical",\n'
    '        "toxicityLevel": "critical",\n'
    '        "populationDensity": "high",\n'
    '        "roadType": "arterial_road",\n'
    '        "estimatedWasteKg": 180,\n'
    '        "priorityScore": 170,\n'
    '        "priorityLevel": "critical",\n'
    '        "lastCollectedAt": "2026-05-07T06:00:00+05:30",\n'
    '        "status": "active"\n'
    '      }\n'
    '    ],\n'
    '    "total": 1,\n'
    '    "limit": 50,\n'
    '    "offset": 0\n'
    '  }\n}',
    '{ "success": false, "error": { "code": "UNAUTHORIZED", "message": "Invalid token" } }',
    "Use in admin bin table and map layer. Pass minFillLevel=80 to show only overflowing bins.",
    "Build dynamic WHERE clause from query params. Use PostGIS ST_DWithin if lat/lng/radius provided. "
    "Paginate with LIMIT/OFFSET."
)

# ── EP 6: Create Waste Point ──────────────────────────────
story += ep(
    "POST", "/api/v1/waste-points", "6 · Create Waste Point",
    "Admin creates a new waste point / bin record. Location stored as PostGIS geography point.",
    "JWT — admin",
    None,
    '{\n  "name": "BTM Layout Junction Bin",\n'
    '  "latitude": 12.9166,\n'
    '  "longitude": 77.6101,\n'
    '  "address": "BTM 2nd Stage, 16th Cross, Bengaluru",\n'
    '  "area": "BTM Layout",\n'
    '  "wasteType": "regular_waste",\n'
    '  "toxicityLevel": "low",\n'
    '  "populationDensity": "high",\n'
    '  "roadType": "residential_road",\n'
    '  "estimatedWasteKg": 80,\n'
    '  "fillLevelPercent": 45\n'
    '}',
    '{\n  "success": true,\n  "message": "Waste point created",\n'
    '  "data": {\n'
    '    "wastePointId": "wp_009",\n'
    '    "name": "BTM Layout Junction Bin",\n'
    '    "latitude": 12.9166,\n'
    '    "longitude": 77.6101,\n'
    '    "priorityScore": 55,\n'
    '    "priorityLevel": "normal",\n'
    '    "status": "active",\n'
    '    "createdAt": "2026-05-08T18:30:00+05:30"\n'
    '  }\n}',
    '{ "success": false, "error": { "code": "VALIDATION_ERROR",\n  "message": "latitude must be between -90 and 90",\n  "details": [{ "field": "latitude", "message": "Invalid value" }] } }',
    "Use in admin 'Add Bin' form. On success, add marker to Leaflet map immediately.",
    "Validate with zod. Insert with ST_MakePoint(longitude,latitude)::geography for location column. "
    "Auto-calculate initial priorityScore using the priority formula module."
)

story.append(pb())

# ── EP 7: Citizen Report ──────────────────────────────────
story += ep(
    "POST", "/api/v1/reports", "7 · Submit Citizen Waste Report",
    "Public endpoint. Citizen submits geotagged waste report with optional photo. Rate-limited.",
    "None — PUBLIC (rate-limited: 10 req/min per IP). Multipart/form-data for photo upload.",
    None,
    '// multipart/form-data fields:\n'
    'citizenName:       "Meena Krishnan"     (optional)\n'
    'mobileNumber:      "+919876543210"       (optional, stored hashed)\n'
    'latitude:          "12.9352"\n'
    'longitude:         "77.6245"\n'
    'address:           "Residency Rd, Koramangala, Bengaluru"\n'
    'landmark:          "Near More Supermarket"\n'
    'area:              "Koramangala"\n'
    'geotagSource:      "browser_geolocation"\n'
    'geotagAccuracyM:   "8.5"\n'
    'wasteCategory:     "organic_black_spot"\n'
    'severity:          "high"\n'
    'description:       "Large garbage pile near footpath, no collection in 3 days"\n'
    'photo:             <image file — JPG/PNG, max 5MB>',
    '{\n  "success": true,\n  "message": "Report submitted. Thank you!",\n'
    '  "data": {\n'
    '    "reportId": "rep_014",\n'
    '    "verificationStatus": "pending",\n'
    '    "estimatedReviewTime": "within 2 hours",\n'
    '    "latitude": 12.9352,\n'
    '    "longitude": 77.6245,\n'
    '    "area": "Koramangala",\n'
    '    "createdAt": "2026-05-08T14:22:00+05:30"\n'
    '  }\n}',
    '{ "success": false, "error": { "code": "RATE_LIMITED", "message": "Too many requests. Try again in 60 seconds." } }',
    "Use in Citizen Report Form. Get lat/lng from navigator.geolocation or manual Leaflet pin. "
    "Submit with FormData. Show success toast with reportId.",
    "Use multer for file upload. Upload photo to Supabase Storage → get public URL → store in DB. "
    "Hash mobile number with bcrypt. Insert location as ST_MakePoint(lng,lat)::geography. "
    "Set verificationStatus='pending'. Apply rate limiting middleware."
)

# ── EP 8: List Reports ────────────────────────────────────
story += ep(
    "GET", "/api/v1/reports", "8 · List Citizen Reports (Admin)",
    "Returns paginated list of citizen reports for admin verification queue.",
    "JWT — admin | supervisor",
    "?verificationStatus=pending\n?severity=high,critical\n?area=Koramangala\n?dateFrom=2026-05-01&dateTo=2026-05-08\n?limit=20&offset=0",
    None,
    '{\n  "success": true,\n  "data": {\n'
    '    "reports": [\n'
    '      {\n'
    '        "reportId": "rep_014",\n'
    '        "area": "Koramangala",\n'
    '        "address": "Residency Rd, Koramangala",\n'
    '        "landmark": "Near More Supermarket",\n'
    '        "latitude": 12.9352,\n'
    '        "longitude": 77.6245,\n'
    '        "wasteCategory": "organic_black_spot",\n'
    '        "severity": "high",\n'
    '        "description": "Large garbage pile, 3 days uncollected",\n'
    '        "photoUrl": "https://storage.supabase.co/citizen_photos/rep_014.jpg",\n'
    '        "verificationStatus": "pending",\n'
    '        "createdAt": "2026-05-08T14:22:00+05:30"\n'
    '      }\n'
    '    ],\n'
    '    "total": 1,\n'
    '    "limit": 20,\n'
    '    "offset": 0\n'
    '  }\n}',
    '{ "success": false, "error": { "code": "UNAUTHORIZED", "message": "Invalid token" } }',
    "Display in Admin Verification Queue table. Show photo thumbnail from photoUrl. "
    "Add Verify/Reject buttons per row. Apply status filter tabs.",
    "Query citizen_reports table. Filter by verificationStatus. JOIN with areas if needed. "
    "Do NOT expose hashed mobile numbers in response."
)

story.append(pb())

# ── EP 9 & 10: Verify / Reject ────────────────────────────
story += ep(
    "PATCH", "/api/v1/reports/:reportId/verify", "9 · Verify Citizen Report",
    "Admin marks a report as verified. Automatically creates a Hotspot record from the report data.",
    "JWT — admin | supervisor",
    None,
    '{\n  "adminRemarks": "Confirmed on-site, critical biomedical waste"\n}',
    '{\n  "success": true,\n  "message": "Report verified and hotspot created",\n'
    '  "data": {\n'
    '    "reportId": "rep_014",\n'
    '    "verificationStatus": "verified",\n'
    '    "generatedHotspotId": "hotspot_012",\n'
    '    "hotspot": {\n'
    '      "hotspotId": "hotspot_012",\n'
    '      "wasteType": "organic_black_spot",\n'
    '      "priorityScore": 105,\n'
    '      "priorityLevel": "critical",\n'
    '      "status": "active",\n'
    '      "area": "Koramangala"\n'
    '    },\n'
    '    "verifiedAt": "2026-05-08T15:00:00+05:30"\n'
    '  }\n}',
    '{ "success": false, "error": { "code": "NOT_FOUND", "message": "Report rep_999 not found" } }',
    "On success, add new hotspot marker to Leaflet map. Update report row status badge to 'Verified'.",
    "Update citizen_reports.verificationStatus = 'verified'. "
    "INSERT new record into hotspots table copying lat/lng/wasteType/severity. "
    "Auto-run priority calculation. Return both updated report and new hotspot."
)

story += ep(
    "PATCH", "/api/v1/reports/:reportId/reject", "10 · Reject Citizen Report",
    "Admin rejects a report (duplicate, spam, or wrong location).",
    "JWT — admin | supervisor",
    None,
    '{\n  "adminRemarks": "Duplicate report — already logged as hotspot_008"\n}',
    '{\n  "success": true,\n  "message": "Report rejected",\n'
    '  "data": {\n'
    '    "reportId": "rep_014",\n'
    '    "verificationStatus": "rejected",\n'
    '    "adminRemarks": "Duplicate report",\n'
    '    "updatedAt": "2026-05-08T15:05:00+05:30"\n'
    '  }\n}',
    '{ "success": false, "error": { "code": "NOT_FOUND", "message": "Report not found" } }',
    "Update report row status badge to 'Rejected'. Remove from pending count.",
    "Update verificationStatus = 'rejected'. No hotspot created. Log adminRemarks."
)

story.append(pb())

# ── EP 11: Image Detection ────────────────────────────────
story += ep(
    "POST", "/api/v1/detections/image", "11 · Image Detection (YOLOv8)",
    "Upload bin image. Calls Roboflow/YOLOv8 API for overflow detection. Auto-creates hotspot if fill >= 80%.",
    "None — PUBLIC (rate-limited). Multipart/form-data.",
    None,
    '// multipart/form-data:\n'
    'image:      <JPG/PNG file, max 10MB>\n'
    'latitude:   "12.9784"\n'
    'longitude:  "77.6408"\n'
    'address:    "100 Feet Rd, Indiranagar"  (optional)\n'
    'sourceType: "citizen_upload"',
    '{\n  "success": true,\n  "message": "Image analysed successfully",\n'
    '  "data": {\n'
    '    "detectionId": "det_003",\n'
    '    "imageUrl": "https://storage.supabase.co/detections/det_003.jpg",\n'
    '    "fillLevelPercent": 92,\n'
    '    "isOverflowing": true,\n'
    '    "isSpilling": true,\n'
    '    "isBinTipped": false,\n'
    '    "detectedWasteType": "mixed_waste",\n'
    '    "confidence": 0.89,\n'
    '    "boundingBoxes": [\n'
    '      { "class": "bin", "x": 120, "y": 45, "width": 210, "height": 300, "confidence": 0.91 }\n'
    '    ],\n'
    '    "isHotspotCreated": true,\n'
    '    "generatedHotspotId": "hotspot_013"\n'
    '  }\n}',
    '{ "success": false, "error": { "code": "DETECTION_FAILED", "message": "No bin detected in image. Try a clearer photo." } }',
    "Display bounding box overlay on the uploaded image preview. Show fill level gauge. "
    "If isOverflowing=true, show 'Hotspot Created' badge.",
    "Upload image to Supabase Storage first. Call Roboflow Inference API with image URL. "
    "Parse response for fill level and labels. If fillLevelPercent >= 80, auto-insert hotspot record. "
    "Store boundingBoxes as JSONB."
)

# ── EP 12: Text Complaint ─────────────────────────────────
story += ep(
    "POST", "/api/v1/complaints/text", "12 · Text Complaint / NLP",
    "Submit raw text complaint from WhatsApp or Twitter. NLP extracts location, waste type, severity.",
    "None — PUBLIC (rate-limited). JSON body.",
    None,
    '{\n  "source": "whatsapp",\n'
    '  "rawText": "Garbage overflowing near Ejipura signal for 2 days. Very bad smell. Biomedical waste visible.",\n'
    '  "senderHash": "sha256_of_phone"\n'
    '}',
    '{\n  "success": true,\n  "message": "Complaint processed",\n'
    '  "data": {\n'
    '    "complaintId": "cmp_007",\n'
    '    "source": "whatsapp",\n'
    '    "extractedLocationText": "Ejipura signal",\n'
    '    "latitude": 12.9510,\n'
    '    "longitude": 77.6245,\n'
    '    "geocodingMethod": "landmark_lookup",\n'
    '    "extractedSeverity": "high",\n'
    '    "wasteKeywords": ["overflowing", "bad smell", "biomedical waste"],\n'
    '    "predictedWasteType": "hospital_biomedical",\n'
    '    "confidenceScore": 0.82,\n'
    '    "isHotspotCreated": true,\n'
    '    "generatedHotspotId": "hotspot_014"\n'
    '  }\n}',
    '{ "success": false, "error": { "code": "VALIDATION_ERROR", "message": "rawText must be at least 10 characters" } }',
    "Show NLP result card with extracted keywords and predicted waste type. "
    "Highlight matched keywords in the original text.",
    "Run keyword extraction pipeline: regex match on waste keyword list → score severity. "
    "Use landmark geocoding DB (pre-built Bangalore landmark → coords map) or Nominatim. "
    "If confidence >= 0.7 and location found, auto-create hotspot. Sanitize input."
)

story.append(pb())

# ── EP 13: Priority Calculate ─────────────────────────────
story += ep(
    "POST", "/api/v1/priority/calculate", "13 · Calculate Priority Score",
    "Calculate or recalculate the priority score for a hotspot. Returns full explainable breakdown.",
    "JWT — admin | supervisor",
    None,
    '{\n  "hotspotId": "hotspot_001",\n'
    '  "wasteType": "hospital_biomedical",\n'
    '  "fillLevelPercent": 95,\n'
    '  "hoursOverflow": 18,\n'
    '  "populationDensity": "high",\n'
    '  "citizenSeverity": "high",\n'
    '  "toxicityLevel": "critical",\n'
    '  "isMonsoonSeason": false\n'
    '}',
    '{\n  "success": true,\n  "data": {\n'
    '    "hotspotId": "hotspot_001",\n'
    '    "scoreBreakdown": {\n'
    '      "baseWasteTypeScore": 100,\n'
    '      "timeOverflowPenalty": 15,\n'
    '      "populationDensityBoost": 15,\n'
    '      "citizenSeverityBoost": 20,\n'
    '      "toxicityBoost": 20\n'
    '    },\n'
    '    "finalPriorityScore": 170,\n'
    '    "priorityLevel": "critical",\n'
    '    "markerColor": "red",\n'
    '    "explanation": "hospital_biomedical base(100) + 18hr overflow(+15) + high density(+15) + high severity(+20) + critical toxicity(+20) = 170 [CRITICAL]",\n'
    '    "calculatedAt": "2026-05-08T18:30:00+05:30"\n'
    '  }\n}',
    '{ "success": false, "error": { "code": "VALIDATION_ERROR", "message": "wasteType is required" } }',
    "Display score breakdown in a visual bar chart per component. Show explanation string in tooltip.",
    "Implement as pure calculation function — no DB read needed. Return detailed breakdown. "
    "Save result to priority_scores table. Update hotspot.priorityScore and hotspot.priorityLevel."
)

# ── EP 14: Route Optimize ─────────────────────────────────
story += ep(
    "POST", "/api/v1/routes/optimize", "14 · Trigger Route Optimization",
    "Triggers slime mold route optimization. Returns jobId immediately (async). Poll job status via EP 15.",
    "JWT — admin",
    None,
    '{\n  "routeDate": "2026-05-09",\n'
    '  "depotIds": ["depot_ejipura", "depot_btm"],\n'
    '  "truckIds": ["truck_001", "truck_002"],\n'
    '  "includeCitizenReports": true,\n'
    '  "includeImageDetections": true,\n'
    '  "optimizationMode": "balanced",\n'
    '  "algorithm": "physarum_slime_mold",\n'
    '  "constraints": {\n'
    '    "maxTruckCapacityKg": 3000,\n'
    '    "maxStopsPerTruck": 25,\n'
    '    "avoidNarrowLanesAfter": "07:30",\n'
    '    "minimizeUTurns": true,\n'
    '    "preferLoopRoutes": true\n'
    '  }\n'
    '}',
    '{\n  "success": true,\n  "message": "Route optimization started",\n'
    '  "data": {\n'
    '    "jobId": "opt_job_001",\n'
    '    "status": "queued",\n'
    '    "routeDate": "2026-05-09",\n'
    '    "totalHotspotsLoaded": 14,\n'
    '    "estimatedCompletionSeconds": 8,\n'
    '    "pollUrl": "/api/v1/routes/optimization-jobs/opt_job_001"\n'
    '  }\n}',
    '{ "success": false, "error": { "code": "OPTIMIZATION_FAILED", "message": "No verified active hotspots found for 2026-05-09" } }',
    "On trigger, store jobId. Start polling EP 15 every 2s. Show progress spinner. "
    "On completed status, fetch tomorrow-plan (EP 16) and render routes on map.",
    "Insert job record with status='queued'. Spawn async worker (setImmediate or worker_threads). "
    "Load active verified hotspots from DB. Build ORS distance matrix. Run Physarum algorithm. "
    "Save routes + stops to DB. Update job status to completed."
)

story.append(pb())

# ── EP 15: Job Status ─────────────────────────────────────
story += ep(
    "GET", "/api/v1/routes/optimization-jobs/:jobId", "15 · Poll Optimization Job Status",
    "Poll the status of an async route optimization job. Frontend polls every 2s until completed or failed.",
    "JWT — admin | supervisor",
    None, None,
    '{\n  "success": true,\n  "data": {\n'
    '    "jobId": "opt_job_001",\n'
    '    "status": "completed",\n'
    '    "routeDate": "2026-05-09",\n'
    '    "algorithm": "physarum_slime_mold",\n'
    '    "totalHotspotsConsidered": 14,\n'
    '    "totalRoutesGenerated": 2,\n'
    '    "startedAt": "2026-05-08T20:00:00+05:30",\n'
    '    "completedAt": "2026-05-08T20:00:08+05:30",\n'
    '    "resultSummary": {\n'
    '      "totalDistanceKm": 56.8,\n'
    '      "totalStops": 14,\n'
    '      "criticalHotspotsCovered": 4,\n'
    '      "estimatedFuelLiters": 10.92,\n'
    '      "estimatedCO2Kg": 29.2\n'
    '    },\n'
    '    "errorMessage": null\n'
    '  }\n}',
    '{ "success": false, "error": { "code": "NOT_FOUND", "message": "Job opt_job_999 not found" } }',
    "Poll with setInterval(2000). On status='completed', stop polling and call GET /tomorrow-plan. "
    "On status='failed', show error toast with errorMessage.",
    "Simple SELECT from route_optimization_jobs by jobId. Return current status and resultSummary."
)

# ── EP 16: Tomorrow Plan ──────────────────────────────────
story += ep(
    "GET", "/api/v1/routes/tomorrow-plan", "16 · Tomorrow's Complete Route Plan",
    "Returns full next-day plan: both static and optimized routes, stops, ETAs, savings.",
    "JWT — admin | supervisor | driver",
    "?routeDate=2026-05-09",
    None,
    '{\n  "success": true,\n  "data": {\n'
    '    "routeDate": "2026-05-09",\n'
    '    "generatedAt": "2026-05-08T20:00:08+05:30",\n'
    '    "status": "planned",\n'
    '    "routes": [\n'
    '      {\n'
    '        "routeId": "route_opt_001",\n'
    '        "routeType": "optimized",\n'
    '        "assignedTruck": { "truckId": "truck_001", "vehicleNumber": "KA01AB1234" },\n'
    '        "assignedDepot": { "depotId": "depot_ejipura", "name": "Ejipura Depot" },\n'
    '        "totalDistanceKm": 28.4,\n'
    '        "estimatedDurationMin": 195,\n'
    '        "estimatedFuelLiters": 5.46,\n'
    '        "estimatedCO2Kg": 14.6,\n'
    '        "totalWasteKg": 1840,\n'
    '        "totalStops": 8,\n'
    '        "polyline": {\n'
    '          "type": "LineString",\n'
    '          "coordinates": [[77.6245,12.9510],[77.6408,12.9784],[77.6412,12.9352]]\n'
    '        },\n'
    '        "stops": [\n'
    '          {\n'
    '            "stopId": "stop_001",\n'
    '            "sequenceNumber": 1,\n'
    '            "address": "100 Feet Rd, Indiranagar",\n'
    '            "area": "Indiranagar",\n'
    '            "wasteType": "hospital_biomedical",\n'
    '            "priorityLevel": "critical",\n'
    '            "priorityScore": 170,\n'
    '            "estimatedPickupKg": 180,\n'
    '            "eta": "2026-05-09T06:00:00+05:30",\n'
    '            "serviceTimeMinutes": 20,\n'
    '            "specialNote": "Biomedical — PPE required",\n'
    '            "status": "pending"\n'
    '          }\n'
    '        ]\n'
    '      }\n'
    '    ],\n'
    '    "savings": {\n'
    '      "distanceSavedKm": 8.3,\n'
    '      "timeSavedMinutes": 50,\n'
    '      "fuelSavedLiters": 1.6,\n'
    '      "co2ReducedKg": 4.3,\n'
    '      "uTurnsReduced": 7,\n'
    '      "criticalHotspotsCovered": 4\n'
    '    }\n'
    '  }\n}',
    '{ "success": false, "error": { "code": "NOT_FOUND", "message": "No route plan for 2026-05-09. Run optimization first." } }',
    "Render optimized routes as blue solid lines, static as grey dashed. "
    "Show stops list as scrollable sidebar. Display savings in stat cards. "
    "Drivers see only their assigned route.",
    "JOIN routes + route_stops + trucks + depots. Filter by routeDate and status != cancelled. "
    "Include both static and optimized route types. Calculate savings by comparing static vs optimized distance/fuel."
)

story.append(pb())

# ── EP 17: Trucks ─────────────────────────────────────────
story += ep(
    "GET", "/api/v1/trucks", "17 · List All Trucks",
    "Returns all trucks with current status and assignment. Used in dashboard truck panel.",
    "JWT — admin | supervisor",
    "?status=available,assigned\n?depotId=depot_ejipura",
    None,
    '{\n  "success": true,\n  "data": {\n'
    '    "trucks": [\n'
    '      {\n'
    '        "truckId": "truck_001",\n'
    '        "vehicleNumber": "KA01AB1234",\n'
    '        "capacityKg": 3000,\n'
    '        "currentLoadKg": 0,\n'
    '        "status": "assigned",\n'
    '        "assignedRouteId": "route_opt_001",\n'
    '        "fuelEfficiencyKmL": 5.2,\n'
    '        "lastUpdatedAt": "2026-05-08T18:00:00+05:30"\n'
    '      },\n'
    '      {\n'
    '        "truckId": "truck_002",\n'
    '        "vehicleNumber": "KA01AB5678",\n'
    '        "capacityKg": 3000,\n'
    '        "currentLoadKg": 0,\n'
    '        "status": "available",\n'
    '        "assignedRouteId": null,\n'
    '        "fuelEfficiencyKmL": 5.0,\n'
    '        "lastUpdatedAt": "2026-05-08T17:30:00+05:30"\n'
    '      }\n'
    '    ],\n'
    '    "total": 2\n'
    '  }\n}',
    '{ "success": false, "error": { "code": "UNAUTHORIZED", "message": "Invalid token" } }',
    "Show in truck assignment panel. Color-code status: green=available, blue=assigned, orange=active.",
    "SELECT from trucks table. Do NOT return sensitive driver personal info here."
)

# ── EP 18: Update Truck Location ──────────────────────────
story += ep(
    "PATCH", "/api/v1/trucks/:truckId/location", "18 · Update Truck Location (→ Firebase)",
    "Driver/GPS device updates truck coordinates. Writes to Firebase Realtime DB for live map. Also syncs to Supabase trucks table.",
    "JWT — driver | admin",
    None,
    '{\n  "latitude": 12.9621,\n'
    '  "longitude": 77.6380,\n'
    '  "speed": 22,\n'
    '  "heading": 145,\n'
    '  "routeProgressPercent": 35,\n'
    '  "currentStopIndex": 4,\n'
    '  "driverStatus": "active"\n'
    '}',
    '{\n  "success": true,\n  "message": "Truck location updated",\n'
    '  "data": {\n'
    '    "truckId": "truck_001",\n'
    '    "latitude": 12.9621,\n'
    '    "longitude": 77.6380,\n'
    '    "updatedAt": "2026-05-09T07:15:00+05:30",\n'
    '    "firebaseSync": true\n'
    '  }\n}',
    '{ "success": false, "error": { "code": "NOT_FOUND", "message": "Truck truck_999 not found" } }',
    "Frontend subscribes to Firebase /liveTrucks/{truckId} directly for realtime position. "
    "This endpoint is called by the driver app, not the dashboard.",
    "Write to Firebase Realtime DB via Firebase Admin SDK: /liveTrucks/{truckId}. "
    "Also UPDATE trucks SET location=ST_MakePoint(lng,lat)::geography, lastUpdatedAt=now(). "
    "Validate driver owns this truck via JWT claims."
)

story.append(pb())

# ── EP 19: Analytics Savings ──────────────────────────────
story += ep(
    "GET", "/api/v1/analytics/savings", "19 · Analytics & Savings",
    "Returns route savings and carbon analytics for the dashboard sidebar.",
    "JWT — admin | supervisor",
    "?dateFrom=2026-05-01&dateTo=2026-05-08\n?area=Indiranagar",
    None,
    '{\n  "success": true,\n  "data": {\n'
    '    "period": { "from": "2026-05-01", "to": "2026-05-08" },\n'
    '    "summary": {\n'
    '      "totalDistanceSavedKm": 58.1,\n'
    '      "totalFuelSavedLiters": 11.2,\n'
    '      "totalCO2ReducedKg": 30.1,\n'
    '      "totalTimeSavedMinutes": 350,\n'
    '      "totalUTurnsReduced": 49,\n'
    '      "criticalHotspotsResolved": 28,\n'
    '      "citizenReportsActedOn": 18\n'
    '    },\n'
    '    "daily": [\n'
    '      {\n'
    '        "date": "2026-05-08",\n'
    '        "distanceSavedKm": 8.3,\n'
    '        "fuelSavedLiters": 1.6,\n'
    '        "co2ReducedKg": 4.3,\n'
    '        "criticalHotspotsResolved": 4\n'
    '      }\n'
    '    ],\n'
    '    "topAreas": [\n'
    '      { "area": "Indiranagar", "hotspots": 6, "priorityScore": 170 },\n'
    '      { "area": "HSR Layout", "hotspots": 4, "priorityScore": 145 }\n'
    '    ]\n'
    '  }\n}',
    '{ "success": false, "error": { "code": "UNAUTHORIZED", "message": "Invalid token" } }',
    "Render summary stats in sidebar cards. Plot daily array in a Recharts/Chart.js bar chart. "
    "Show topAreas as a ranked list.",
    "Aggregate from analytics_summaries table. If no cached summary, compute from routes + route_comparisons tables. "
    "Cache aggregated result for 5 minutes."
)

story.append(pb())

# ── SECTION 10: SAMPLE MOCK DATASET ───────────────────────
story += section_header("10 · Sample Mock Dataset")
story += [
    P("Seed this data into Supabase for the hackathon demo:", body),
    gap(6),
    P("<b>Sample Depots:</b>", h3),
    code_block(
        '[\n'
        '  {\n'
        '    "depotId": "depot_ejipura",\n'
        '    "name": "Ejipura Depot",\n'
        '    "latitude": 12.9510,\n'
        '    "longitude": 77.6245,\n'
        '    "address": "8th Cross, Ejipura, Bengaluru 560047"\n'
        '  },\n'
        '  {\n'
        '    "depotId": "depot_btm",\n'
        '    "name": "BTM Layout Depot",\n'
        '    "latitude": 12.9166,\n'
        '    "longitude": 77.6101,\n'
        '    "address": "16th Cross, BTM 2nd Stage, Bengaluru 560076"\n'
        '  }\n'
        ']'
    ),
    gap(6),
    P("<b>Sample Trucks:</b>", h3),
    code_block(
        '[\n'
        '  { "truckId": "truck_001", "vehicleNumber": "KA01AB1234",\n'
        '    "capacityKg": 3000, "status": "available", "depotId": "depot_ejipura" },\n'
        '  { "truckId": "truck_002", "vehicleNumber": "KA01AB5678",\n'
        '    "capacityKg": 3000, "status": "available", "depotId": "depot_ejipura" },\n'
        '  { "truckId": "truck_003", "vehicleNumber": "KA01CD9012",\n'
        '    "capacityKg": 3000, "status": "available", "depotId": "depot_btm" }\n'
        ']'
    ),
    gap(6),
    P("<b>Sample Hotspots (8 Bangalore locations):</b>", h3),
    code_block(
        '[\n'
        '  { "hotspotId":"hotspot_001", "area":"Indiranagar",\n'
        '    "lat":12.9784, "lng":77.6408, "wasteType":"hospital_biomedical",\n'
        '    "fill":95, "toxicity":"critical", "density":"high", "priorityScore":170 },\n'
        '\n'
        '  { "hotspotId":"hotspot_002", "area":"HSR Layout",\n'
        '    "lat":12.9116, "lng":77.6473, "wasteType":"organic_black_spot",\n'
        '    "fill":88, "toxicity":"moderate", "density":"high", "priorityScore":128 },\n'
        '\n'
        '  { "hotspotId":"hotspot_003", "area":"Peenya Industrial",\n'
        '    "lat":13.0284, "lng":77.5165, "wasteType":"chemical_industrial",\n'
        '    "fill":72, "toxicity":"high", "density":"medium", "priorityScore":138 },\n'
        '\n'
        '  { "hotspotId":"hotspot_004", "area":"Koramangala",\n'
        '    "lat":12.9352, "lng":77.6245, "wasteType":"mixed_waste",\n'
        '    "fill":85, "toxicity":"low", "density":"very_high", "priorityScore":95 },\n'
        '\n'
        '  { "hotspotId":"hotspot_005", "area":"Bellandur",\n'
        '    "lat":12.9254, "lng":77.6784, "wasteType":"plastic_dry",\n'
        '    "fill":78, "toxicity":"low", "density":"medium", "priorityScore":68 },\n'
        '\n'
        '  { "hotspotId":"hotspot_006", "area":"Electronic City",\n'
        '    "lat":12.8399, "lng":77.6770, "wasteType":"e_waste",\n'
        '    "fill":82, "toxicity":"high", "density":"high", "priorityScore":135 },\n'
        '\n'
        '  { "hotspotId":"hotspot_007", "area":"BTM Layout",\n'
        '    "lat":12.9166, "lng":77.6101, "wasteType":"regular_waste",\n'
        '    "fill":90, "toxicity":"low", "density":"high", "priorityScore":75 },\n'
        '\n'
        '  { "hotspotId":"hotspot_008", "area":"Ejipura",\n'
        '    "lat":12.9510, "lng":77.6295, "wasteType":"organic_black_spot",\n'
        '    "fill":92, "toxicity":"moderate", "density":"very_high", "priorityScore":120 }\n'
        ']'
    ),
    gap(8), pb(),
]

# ── SECTION 11: SUPABASE SCHEMA ───────────────────────────
story += section_header("11 · Supabase / PostGIS Table Summary")
story += [
    code_block(
        "-- Enable PostGIS on Supabase\n"
        "CREATE EXTENSION IF NOT EXISTS postgis;\n\n"
        "-- Trucks\n"
        "CREATE TABLE trucks (\n"
        "  truck_id        VARCHAR PRIMARY KEY,\n"
        "  vehicle_number  VARCHAR NOT NULL,\n"
        "  capacity_kg     INTEGER DEFAULT 3000,\n"
        "  current_load_kg INTEGER DEFAULT 0,\n"
        "  status          VARCHAR DEFAULT 'available',\n"
        "  assigned_route_id VARCHAR,\n"
        "  fuel_efficiency_kml FLOAT DEFAULT 5.2,\n"
        "  location        geography(Point, 4326),\n"
        "  last_updated_at TIMESTAMPTZ DEFAULT now(),\n"
        "  created_at      TIMESTAMPTZ DEFAULT now()\n"
        ");\n\n"
        "-- Depots\n"
        "CREATE TABLE depots (\n"
        "  depot_id        VARCHAR PRIMARY KEY,\n"
        "  name            VARCHAR NOT NULL,\n"
        "  address         TEXT,\n"
        "  location        geography(Point, 4326) NOT NULL,\n"
        "  latitude        FLOAT NOT NULL,\n"
        "  longitude       FLOAT NOT NULL,\n"
        "  capacity_trucks INTEGER DEFAULT 10\n"
        ");\n\n"
        "-- Waste Points\n"
        "CREATE TABLE waste_points (\n"
        "  waste_point_id  VARCHAR PRIMARY KEY,\n"
        "  name            VARCHAR,\n"
        "  location        geography(Point, 4326) NOT NULL,\n"
        "  latitude        FLOAT NOT NULL,\n"
        "  longitude       FLOAT NOT NULL,\n"
        "  address         TEXT,\n"
        "  area            VARCHAR,\n"
        "  fill_level_pct  INTEGER CHECK (fill_level_pct BETWEEN 0 AND 100),\n"
        "  waste_type      VARCHAR NOT NULL,\n"
        "  toxicity_level  VARCHAR DEFAULT 'low',\n"
        "  population_density VARCHAR DEFAULT 'medium',\n"
        "  road_type       VARCHAR DEFAULT 'residential_road',\n"
        "  estimated_waste_kg FLOAT DEFAULT 0,\n"
        "  priority_score  FLOAT DEFAULT 0,\n"
        "  priority_level  VARCHAR DEFAULT 'normal',\n"
        "  last_collected_at TIMESTAMPTZ,\n"
        "  status          VARCHAR DEFAULT 'active',\n"
        "  created_at      TIMESTAMPTZ DEFAULT now()\n"
        ");\n"
        "CREATE INDEX ON waste_points USING GIST(location);\n\n"
        "-- Citizen Reports\n"
        "CREATE TABLE citizen_reports (\n"
        "  report_id       VARCHAR PRIMARY KEY,\n"
        "  citizen_name    VARCHAR,\n"
        "  mobile_hash     VARCHAR,\n"
        "  location        geography(Point, 4326) NOT NULL,\n"
        "  latitude        FLOAT NOT NULL,\n"
        "  longitude       FLOAT NOT NULL,\n"
        "  address         TEXT,\n"
        "  landmark        VARCHAR,\n"
        "  area            VARCHAR,\n"
        "  geotag_source   VARCHAR,\n"
        "  geotag_accuracy_m FLOAT,\n"
        "  waste_category  VARCHAR,\n"
        "  severity        VARCHAR DEFAULT 'medium',\n"
        "  description     TEXT,\n"
        "  photo_url       TEXT,\n"
        "  verification_status VARCHAR DEFAULT 'pending',\n"
        "  admin_remarks   TEXT,\n"
        "  generated_hotspot_id VARCHAR,\n"
        "  created_at      TIMESTAMPTZ DEFAULT now(),\n"
        "  verified_at     TIMESTAMPTZ\n"
        ");\n"
        "CREATE INDEX ON citizen_reports USING GIST(location);\n\n"
        "-- Hotspots\n"
        "CREATE TABLE hotspots (\n"
        "  hotspot_id      VARCHAR PRIMARY KEY,\n"
        "  source_type     VARCHAR NOT NULL,\n"
        "  source_id       VARCHAR,\n"
        "  location        geography(Point, 4326) NOT NULL,\n"
        "  latitude        FLOAT NOT NULL,\n"
        "  longitude       FLOAT NOT NULL,\n"
        "  address         TEXT,\n"
        "  area            VARCHAR,\n"
        "  waste_type      VARCHAR NOT NULL,\n"
        "  fill_level_pct  INTEGER,\n"
        "  estimated_waste_kg FLOAT,\n"
        "  toxicity_level  VARCHAR DEFAULT 'low',\n"
        "  population_density VARCHAR DEFAULT 'medium',\n"
        "  road_type       VARCHAR DEFAULT 'residential_road',\n"
        "  priority_score  FLOAT DEFAULT 0,\n"
        "  priority_level  VARCHAR DEFAULT 'normal',\n"
        "  status          VARCHAR DEFAULT 'active',\n"
        "  created_at      TIMESTAMPTZ DEFAULT now(),\n"
        "  verified_at     TIMESTAMPTZ,\n"
        "  collected_at    TIMESTAMPTZ\n"
        ");\n"
        "CREATE INDEX ON hotspots USING GIST(location);\n\n"
        "-- Routes\n"
        "CREATE TABLE routes (\n"
        "  route_id        VARCHAR PRIMARY KEY,\n"
        "  job_id          VARCHAR,\n"
        "  route_type      VARCHAR NOT NULL,\n"
        "  assigned_truck_id VARCHAR,\n"
        "  depot_start_id  VARCHAR,\n"
        "  depot_end_id    VARCHAR,\n"
        "  route_date      DATE NOT NULL,\n"
        "  total_distance_km FLOAT,\n"
        "  estimated_duration_min FLOAT,\n"
        "  estimated_fuel_liters FLOAT,\n"
        "  estimated_co2_kg FLOAT,\n"
        "  total_waste_kg  FLOAT,\n"
        "  total_stops     INTEGER,\n"
        "  route_polyline  JSONB,\n"
        "  status          VARCHAR DEFAULT 'planned',\n"
        "  created_at      TIMESTAMPTZ DEFAULT now()\n"
        ");\n\n"
        "-- Route Stops\n"
        "CREATE TABLE route_stops (\n"
        "  stop_id         VARCHAR PRIMARY KEY,\n"
        "  route_id        VARCHAR REFERENCES routes(route_id),\n"
        "  sequence_number INTEGER NOT NULL,\n"
        "  source_type     VARCHAR,\n"
        "  source_id       VARCHAR,\n"
        "  location        geography(Point, 4326),\n"
        "  latitude        FLOAT,\n"
        "  longitude       FLOAT,\n"
        "  address         TEXT,\n"
        "  area            VARCHAR,\n"
        "  waste_type      VARCHAR,\n"
        "  priority_score  FLOAT,\n"
        "  priority_level  VARCHAR,\n"
        "  estimated_pickup_kg FLOAT,\n"
        "  eta             TIMESTAMPTZ,\n"
        "  service_time_min FLOAT DEFAULT 8,\n"
        "  status          VARCHAR DEFAULT 'pending',\n"
        "  completed_at    TIMESTAMPTZ\n"
        ");\n\n"
        "-- Route Optimization Jobs\n"
        "CREATE TABLE route_optimization_jobs (\n"
        "  job_id          VARCHAR PRIMARY KEY,\n"
        "  route_date      DATE,\n"
        "  algorithm       VARCHAR DEFAULT 'physarum_slime_mold',\n"
        "  status          VARCHAR DEFAULT 'queued',\n"
        "  total_hotspots  INTEGER DEFAULT 0,\n"
        "  total_routes    INTEGER DEFAULT 0,\n"
        "  started_at      TIMESTAMPTZ,\n"
        "  completed_at    TIMESTAMPTZ,\n"
        "  error_message   TEXT,\n"
        "  result_summary  JSONB\n"
        ");\n\n"
        "-- Analytics Summaries\n"
        "CREATE TABLE analytics_summaries (\n"
        "  analytics_id    VARCHAR PRIMARY KEY,\n"
        "  date            DATE UNIQUE,\n"
        "  total_hotspots  INTEGER DEFAULT 0,\n"
        "  critical_hotspots INTEGER DEFAULT 0,\n"
        "  total_reports   INTEGER DEFAULT 0,\n"
        "  total_bins_collected INTEGER DEFAULT 0,\n"
        "  distance_saved_km FLOAT DEFAULT 0,\n"
        "  fuel_saved_liters FLOAT DEFAULT 0,\n"
        "  co2_reduced_kg  FLOAT DEFAULT 0,\n"
        "  avg_collection_delay_min FLOAT DEFAULT 0,\n"
        "  created_at      TIMESTAMPTZ DEFAULT now()\n"
        ");"
    ),
    gap(8), pb(),
]

# ── SECTION 12: FIREBASE STRUCTURE ────────────────────────
story += section_header("12 · Firebase Realtime Database Structure")
story += [
    P("Firebase is used <b>ONLY</b> for live/simulated truck coordinates. "
      "The frontend subscribes directly to this path for realtime map updates.", body),
    gap(6),
    code_block(
        "// Firebase Realtime Database path\n"
        "// Path: /liveTrucks/{truckId}\n\n"
        "{\n"
        '  "liveTrucks": {\n'
        '    "truck_001": {\n'
        '      "truckId": "truck_001",\n'
        '      "currentLatitude": 12.9621,\n'
        '      "currentLongitude": 77.6380,\n'
        '      "currentSpeed": 22,\n'
        '      "currentHeading": 145,\n'
        '      "driverStatus": "active",\n'
        '      "assignedRouteId": "route_opt_001",\n'
        '      "routeProgressPercent": 35,\n'
        '      "currentStopIndex": 4,\n'
        '      "lastUpdatedAt": "2026-05-09T07:15:00+05:30"\n'
        '    },\n'
        '    "truck_002": {\n'
        '      "truckId": "truck_002",\n'
        '      "currentLatitude": 12.9166,\n'
        '      "currentLongitude": 77.6101,\n'
        '      "currentSpeed": 0,\n'
        '      "currentHeading": 0,\n'
        '      "driverStatus": "idle",\n'
        '      "assignedRouteId": null,\n'
        '      "routeProgressPercent": 0,\n'
        '      "currentStopIndex": 0,\n'
        '      "lastUpdatedAt": "2026-05-09T06:00:00+05:30"\n'
        '    }\n'
        '  }\n'
        '}'
    ),
    gap(6),
    P("<b>React Leaflet subscription (firebase SDK):</b>", h3),
    code_block(
        "import { ref, onValue } from 'firebase/database';\n\n"
        "const truckRef = ref(db, 'liveTrucks/truck_001');\n"
        "onValue(truckRef, (snapshot) => {\n"
        "  const data = snapshot.val();\n"
        "  // Update Leaflet marker position\n"
        "  truckMarker.setLatLng([data.currentLatitude, data.currentLongitude]);\n"
        "  setRouteProgress(data.routeProgressPercent);\n"
        "});\n\n"
        "// For simulation: animate truck along route polyline coords\n"
        "// Update Firebase every 3s with next coord from polyline array"
    ),
    gap(8), pb(),
]

# ── SECTION 13: FRONTEND INTEGRATION ─────────────────────
story += section_header("13 · Frontend Integration Notes")

fe_notes = [
    ("Dashboard KPIs", "Fetch GET /dashboard/summary on mount. setInterval 60s refresh. "
     "Show in Tailwind stat cards with color coding (red=critical, green=available)."),
    ("Map Initialization", "Initialize Leaflet map centered at Bengaluru [12.9716, 77.5946] zoom 12. "
     "Use dark tile layer: CartoDB DarkMatter."),
    ("Hotspot Markers", "GET /map/markers → loop markers array → L.circleMarker(lat,lng, {color: markerColor}). "
     "Bind L.popup with popupData fields. Filter by type checkboxes."),
    ("Route Polylines", "GET /map/routes → L.geoJSON(polyline). Static: grey #94A3B8 dashed. "
     "Optimized: blue #3B82F6 solid weight:4. Toggle with UI switch."),
    ("Citizen Report Form", "navigator.geolocation.getCurrentPosition() for auto location. "
     "Fallback: Leaflet map click → get latlng. Upload with FormData to POST /reports."),
    ("Image Upload", "Use <input type=file accept='image/*'>. Convert to FormData. "
     "POST to /detections/image. Show bounding box overlay on preview."),
    ("Route Optimization", "POST /routes/optimize → store jobId. Poll GET /optimization-jobs/:jobId "
     "every 2000ms. On completed, call GET /routes/tomorrow-plan and re-render map."),
    ("Firebase Truck Tracking", "Subscribe to Firebase /liveTrucks/{truckId}. "
     "Move Leaflet marker smoothly on each update. Show route progress bar in sidebar."),
    ("Savings Sidebar", "GET /analytics/savings. Show distanceSavedKm, fuelSavedLiters, CO2 as animated counters."),
    ("Auth Flow", "Store accessToken in memory (not localStorage). Store refreshToken in httpOnly cookie. "
     "Axios interceptor auto-refreshes on 401. React-Router guards for role-based routes."),
]

for screen, note in fe_notes:
    story.append(P(f"<b>{screen}:</b> {note}", body_dim))
    story.append(gap(3))

story += [gap(8), pb()]

# ── SECTION 14: EXCLUDED FROM MVP ─────────────────────────
story += section_header("14 · Intentionally Excluded from MVP")
story += [
    P("The following are production extensions — not needed for hackathon demo:", body),
    gap(6),
]

excluded = [
    ("Swagger/OpenAPI YAML", "Auto-generate post-hackathon with swagger-jsdoc + swagger-ui-express"),
    ("pgRouting", "Advanced graph routing inside PostgreSQL — use ORS API instead for MVP"),
    ("Kafka / MQTT fleet stream", "Use Firebase Realtime DB for simulated truck tracking"),
    ("Redis caching layer", "Use in-memory JS object cache (TTL 30s) for MVP"),
    ("WhatsApp Business API", "Simulate with POST /complaints/text manually for demo"),
    ("Twitter/X streaming API", "Simulate with test text complaints for demo"),
    ("Driver mobile app", "Use admin web UI to simulate driver stop completion"),
    ("Admin route approval workflow", "Routes go straight to 'planned' in MVP — add approve/dispatch step post-hackathon"),
    ("Segregation compliance area polygons", "Hardcode compliance levels per area in MVP — no polygon UI needed"),
    ("OR-Tools VRP comparison", "Physarum slime mold only for MVP — OR-Tools is production comparison"),
    ("Monsoon season API", "Hardcode isMonsoonSeason flag in .env for demo purposes"),
    ("Full audit log / change history", "Add CREATED/UPDATED event log table post-hackathon"),
    ("Webhook signature verification", "Skip HMAC validation for simulated webhooks in demo"),
    ("Push notifications to citizens", "Add Firebase Cloud Messaging post-hackathon"),
]

ex_data = [["Feature","Production Extension Note"]] + [[f,n] for f,n in excluded]
ts_ex = TableStyle([
    ("BACKGROUND",(0,0),(-1,0),DARK_BG),("TEXTCOLOR",(0,0),(-1,0),ORANGE),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),
    ("TEXTCOLOR",(0,1),(0,-1),TEXT_MAIN),("FONTNAME",(0,1),(0,-1),"Helvetica-Bold"),
    ("TEXTCOLOR",(1,1),(1,-1),TEXT_DIM),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[CODE_BG,MUTED_BG]),
    ("GRID",(0,0),(-1,-1),0.3,MUTED_BG),
    ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
    ("LEFTPADDING",(0,0),(-1,-1),8),
])
story.append(Table(ex_data, colWidths=[150,doc.width-150], style=ts_ex))

story += [
    gap(20),
    Table([[
        Paragraph("BioRoute MVP API Contract — Ready to Build",
                  S("Footer", fontSize=10, textColor=TEXT_DIM, fontName="Helvetica",
                    alignment=TA_CENTER, leading=14))
    ]], colWidths=[doc.width],
         style=TableStyle([("BACKGROUND",(0,0),(-1,-1),DARK_BG),
                           ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10)]))
]

# ── BUILD ─────────────────────────────────────────────────
doc.build(story)
print("✅ PDF generated: BioRoute_MVP_API_Contract.pdf")
