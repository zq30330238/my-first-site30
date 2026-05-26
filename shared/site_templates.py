"""Site template engine — load templates, inject variables, wrap AI-generated content.

Global values centralized here. Change once, apply everywhere.
"""

import re
import random
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "shared" / "templates"

# Global values used across all sites
GLOBALS = {
    "email": "contact@jycsd.com",
    "ga4_id": "G-GGNWR1X1GV",
    "adsense_pub": "ca-pub-2595917642864488",
    "year": str(datetime.now().year),
}

SITE_CONFIG = {
    "sub-pets": {
        "brand": "PetCareHub",
        "domain": "pets.jycsd.com",
        "category": "Pet Care",
        "brandColor": "orange-600",
        "brandHex": "#ea580c",
        "tailwindColors": """brand: {50: '#fff7ed', 100: '#ffedd5', 200: '#fed7aa', 400: '#fb923c', 500: '#f97316', 600: '#ea580c', 700: '#c2410c', 800: '#9a3412'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#f97316",
        "blockquoteBg": "#fff7ed",
        "related_articles": [
            ("article-11.html", "Pet Emergencies: What Every Owner Must Know Before Disaster Strikes"),
            ("article-27.html", "Pet First Aid Kit: Essential Supplies Every Owner Needs"),
            ("article-3.html", "How to Care for a New Puppy: First Month Checklist"),
        ],
    },
    "sub-healthy": {
        "brand": "HealthyEats",
        "domain": "healthy.jycsd.com",
        "category": "Healthy Eating",
        "brandColor": "green-600",
        "brandHex": "#16a34a",
        "tailwindColors": """brand: {50: '#f0fdf4', 100: '#dcfce7', 200: '#bbf7d0', 400: '#4ade80', 500: '#22c55e', 600: '#16a34a', 700: '#15803d', 800: '#166534'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#22c55e",
        "blockquoteBg": "#f0fdf4",
        "related_articles": [
            ("article-1.html", "10 Superfoods You Should Eat Every Day for Optimal Health"),
            ("article-2.html", "Beginner's Guide to Weekly Meal Prepping: Save Time and Eat Better"),
            ("article-3.html", "How to Build a Balanced Plate at Every Meal Without Counting Calories"),
        ],
    },
    "sub-home": {
        "brand": "HomeNest",
        "domain": "home.jycsd.com",
        "category": "Home & Garden",
        "brandColor": "emerald-700",
        "brandHex": "#047857",
        "tailwindColors": """brand: {50: '#ecfdf5', 100: '#d1fae5', 200: '#a7f3d0', 400: '#34d399', 500: '#10b981', 600: '#059669', 700: '#047857', 800: '#065f46'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#10b981",
        "blockquoteBg": "#ecfdf5",
        "related_articles": [
            ("article-1.html", "15 DIY Home Improvement Projects Under $100"),
            ("article-2.html", "Beginner's Guide to Indoor Plant Care"),
            ("article-3.html", "How to Declutter Your Home: Room-by-Room Guide"),
        ],
    },
    "sub-finance": {
        "brand": "MoneyWise",
        "domain": "finance.jycsd.com",
        "category": "Personal Finance",
        "brandColor": "blue-700",
        "brandHex": "#1d4ed8",
        "tailwindColors": """brand: {50: '#eff6ff', 100: '#dbeafe', 200: '#bfdbfe', 400: '#60a5fa', 500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8', 800: '#1e40af'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#3b82f6",
        "blockquoteBg": "#eff6ff",
        "related_articles": [
            ("article-1.html", "How to Start Investing with $100: A Complete Beginner's Guide"),
            ("article-2.html", "Best High-Yield Savings Accounts: 2026 Comparison Guide"),
            ("article-3.html", "Credit Score Explained: How to Improve Yours Fast"),
        ],
    },
    "sub-tech": {
        "brand": "TechPulse",
        "domain": "tech.jycsd.com",
        "category": "Technology",
        "brandColor": "slate-700",
        "brandHex": "#334155",
        "tailwindColors": """brand: {50: '#f8fafc', 100: '#f1f5f9', 200: '#e2e8f0', 400: '#94a3b8', 500: '#64748b', 600: '#475569', 700: '#334155', 800: '#1e293b'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#64748b",
        "blockquoteBg": "#f8fafc",
        "related_articles": [
            ("article-1.html", "Best Budget Smartphones Under $300 (2026)"),
            ("article-2.html", "How to Build a Home Office Setup for Productivity"),
            ("article-3.html", "AI Tools That Will Change Your Daily Workflow"),
        ],
    },
    "sub-travel": {
        "brand": "TravelScope",
        "domain": "travel.jycsd.com",
        "category": "Travel",
        "brandColor": "cyan-700",
        "brandHex": "#0e7490",
        "tailwindColors": """brand: {50: '#ecfeff', 100: '#cffafe', 200: '#a5f3fc', 400: '#22d3ee', 500: '#06b6d4', 600: '#0891b2', 700: '#0e7490', 800: '#155e75'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#06b6d4",
        "blockquoteBg": "#ecfeff",
        "related_articles": [
            ("article-1.html", "10 Budget Travel Destinations for 2026"),
            ("article-2.html", "How to Find Cheap Flights: Expert Hacks"),
            ("article-3.html", "Solo Travel Guide: Safety Tips & Best Destinations"),
        ],
    },
    "sub-auto": {
        "brand": "AutoPulse",
        "domain": "auto.jycsd.com",
        "category": "Automotive",
        "brandColor": "red-600",
        "brandHex": "#dc2626",
        "tailwindColors": """brand: {50: '#fef2f2', 100: '#fee2e2', 200: '#fecaca', 400: '#f87171', 500: '#ef4444', 600: '#dc2626', 700: '#b91c1c', 800: '#991b1b'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#ef4444",
        "blockquoteBg": "#fef2f2",
        "related_articles": [
            ("article-1.html", "Best Sports Cars Under $50,000 in 2026"),
            ("article-2.html", "EV vs Hybrid vs Plug-in Hybrid: Which Is Right for You?"),
            ("article-3.html", "How to Negotiate a Car Price: 7 Dealer Tactics Exposed"),
        ],
        "predefined_topics": [
            # === Buying (5 topics) ===
            
            {"title": "Car Loan vs Lease: Which Financing Option Saves More Money in 2026", "category": "buying", "angle": "financial comparison guide", "key_points": ["Monthly payment breakdown for loan vs lease with real numbers", "Hidden fees: acquisition fee, disposition fee, mileage penalties", "When leasing makes financial sense and when it doesn't", "Tax implications and business write-off considerations"]},
            {"title": "2026 First-Time Car Buyer Guide: Everything You Need to Know Before Visiting a Dealership", "category": "buying", "angle": "beginner buyer walkthrough", "key_points": ["Budget setting: the 20/4/10 rule explained", "Pre-approval vs dealer financing — which saves more", "Test drive checklist most first-time buyers skip", "Red flags in the finance office and how to push back"]},
            {"title": "Certified Pre-Owned vs Used Car: Is the CPO Premium Worth It in 2026", "category": "buying", "angle": "value analysis comparison", "key_points": ["What CPO certification actually covers vs marketing claims", "Price comparison: CPO vs non-CPO for popular 2023-2024 models", "Extended warranty value: manufacturer-backed vs third-party", "Best CPO programs ranked: Lexus, BMW, Toyota, Honda"]},
            {"title": "The Hidden Costs of Car Ownership Americans Underestimate Every Year", "category": "buying", "angle": "total cost of ownership exposé", "key_points": ["Depreciation as the single biggest cost most buyers ignore", "Insurance, registration, and taxes by state — real annual numbers", "Maintenance and repair costs averaged across 10 popular models", "Fuel/electricity costs: gas vs hybrid vs EV 5-year comparison"]},
            {"title": "How to Read a Used Car History Report and Spot Dealbreakers Before You Buy", "category": "buying", "angle": "inspection skill guide", "key_points": ["CarFax vs AutoCheck: what each report actually covers", "Accident history tiers: minor fender bender vs structural damage", "Title brands explained: salvage, rebuilt, flood, lemon — and why they matter", "Odometer rollback signs and service history gaps that signal trouble"]},
            # === Performance (5 topics) ===
            {"title": "0-60 Under 3 Seconds: The 10 Fastest Accelerating Production Cars of 2026", "category": "performance", "angle": "ranking with technical breakdown", "key_points": ["Ranked list with verified 0-60 times from instrumented testing", "Powertrain breakdown: EV dual/tri-motor vs ICE hybrid vs pure combustion", "Launch control technology comparison across brands", "Tire and traction technology enabling sub-3-second acceleration"]},
            {"title": "Turbocharger vs Supercharger vs Naturally Aspirated: Which Engine Is Right for Your Driving Style", "category": "performance", "angle": "technical buyer's guide", "key_points": ["How each system works with simple diagrams explained in text", "Throttle response, lag, and power delivery differences in real driving", "Reliability and maintenance costs for each type over 100,000 miles", "Best cars for each engine type at $30K, $50K, and $80K price points"]},
            {"title": "The Best Track Day Cars for Beginners: Affordable Performance Machines That Won't Kill You", "category": "performance", "angle": "entry-level motorsport guide", "key_points": ["Selection criteria: forgiving handling, affordable consumables, safety", "Top 5 picks: Mazda MX-5 Miata to Toyota GR86 to Hyundai Elantra N", "Track day costs breakdown: tires, brakes, fluids, insurance, entry fees", "Essential upgrades before your first track day and what to skip"]},
            {"title": "AWD vs RWD vs FWD: Which Drivetrain Actually Delivers the Best Performance on Road and Track", "category": "performance", "angle": "engineering comparison with real test data", "key_points": ["Weight distribution, polar moment, and how drivetrain affects handling balance", "Lap time comparisons: same car platform with different drivetrains", "Wet and dry performance differences supported by instrumented testing", "Tire wear patterns and long-term ownership costs by drivetrain type"]},
            {"title": "How Launch Control Works and Which 2026 Cars Have the Best Systems", "category": "performance", "angle": "technology deep dive", "key_points": ["Engineering behind launch control: ECU mapping, clutch engagement, traction management", "Step-by-step activation for Porsche, BMW M, Tesla, and Nissan GT-R systems", "Does launch control damage your car? Transmission wear data and warranty implications", "Aftermarket launch control options for cars without factory systems"]},
            # === Reviews (3 topics) ===
            {"title": "2026 Honda Civic Hybrid Review: The Perfect Daily Driver for $30,000", "category": "reviews", "angle": "comprehensive owner-perspective review", "key_points": ["Real-world fuel economy: city, highway, and combined MPG from extended testing", "Interior quality, infotainment, and cargo space compared to Corolla and Elantra hybrids", "Driving dynamics: steering feel, ride quality, and NVH at highway speeds", "Total cost of ownership projection over 5 years vs non-hybrid Civic"]},
            {"title": "Tesla Cybertruck 6-Month Long-Term Review: What Owners Aren't Telling You", "category": "reviews", "angle": "long-term ownership report", "key_points": ["Daily livability: parking, maneuverability, and real-world range with payload", "Build quality after 10,000 miles: panel gaps, interior wear, software bugs", "Charging reality: Supercharger speed, home charging costs, cold weather range loss", "Six-month total cost: insurance, electricity, maintenance, and unexpected expenses"]},
            {"title": "2026 Toyota Camry vs Honda Accord: The Midsize Sedan Battle No One Expected to Still Be This Good", "category": "reviews", "angle": "head-to-head comparison", "key_points": ["Powertrain comparison: Camry's hybrid-only lineup vs Accord's hybrid and turbo options", "Interior tech, material quality, and rear-seat comfort measured and compared", "Real-world fuel economy and annual fuel cost projection for 15,000 miles", "Resale value analysis: 3-year and 5-year depreciation projections for both models"]},
            # === Chinese Brands (3 topics) ===
            {"title": "Zeekr 001 Review: Geely's Premium Electric Shooting Brake That Rivals Porsche Taycan Cross Turismo", "category": "chinese-brands", "angle": "premium EV comparison review", "key_points": ["Design and engineering by Geely's global team with former Audi and Bentley talent", "Dual-motor performance specs: 0-60, range, and charging curve data", "Interior quality and tech: materials, screen UX, and driver assistance comparison", "European market pricing and how it undercuts German premium EVs by 30-40%"]},
            {"title": "XPeng G6 Review: The Model Y Competitor with 800V Charging That Actually Works", "category": "chinese-brands", "angle": "technology-focused EV review", "key_points": ["800V SEPA 2.0 platform: real-world charging speed from 10-80% with timer data", "XNGP autonomous driving vs Tesla FSD: capability comparison in urban and highway scenarios", "Build quality, interior space, and ride comfort compared to Model Y and Ioniq 5", "European expansion timeline, pricing, and warranty coverage details"]},
            {"title": "Li Auto L9 Review: China's Best-Selling Large SUV That Americans Can't Buy Yet", "category": "chinese-brands", "angle": "what America is missing spotlight", "key_points": ["Range-extender powertrain explained: why this hybrid approach works for large SUVs", "Interior luxury: 6-seat configuration, rear entertainment, fridge, and massaging seats", "AD Max autonomous driving system: LiDAR + camera fusion real-world performance", "Why Li Auto dominates China's premium SUV market and whether global expansion is planned"]},
        ],
    },
    "sub-moto": {
        "brand": "MotoPulse",
        "domain": "moto.jycsd.com",
        "category": "Motorcycles",
        "brandColor": "orange-500",
        "brandHex": "#f97316",
        "tailwindColors": """brand: {50: '#fff7ed', 100: '#ffedd5', 200: '#fed7aa', 400: '#fb923c', 500: '#f97316', 600: '#ea580c', 700: '#c2410c', 800: '#9a3412'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#f97316",
        "blockquoteBg": "#fff7ed",
        "related_articles": [
            ("article-1.html", "Best Beginner Motorcycles Under $8,000 in 2026"),
            ("article-2.html", "Electric Motorcycle vs Gas: Total Cost of Ownership Compared"),
            ("article-3.html", "Motorcycle Track Day Guide: First Time at the Circuit"),
        ],
        "predefined_topics": [
            # === 10 user-specified topics covering different motorcycle types ===
            {
                "title": "Best Dirt Bikes 2026: Off-Road Motorcycles for Beginners and Pros",
                "category": "buying",
                "angle": "ranked buyer's guide covering off-road bikes for all skill levels",
                "key_points": [
                    "Top 8 dirt bikes ranked by skill level: beginner-friendly 250cc 4-strokes to pro-level 450cc race machines",
                    "Engine types compared: 2-stroke vs 4-stroke — power delivery, maintenance, and best use cases for each",
                    "Key features to look for: suspension travel, seat height, weight, electric start, and adjustable ergonomics",
                    "Budget breakdown: entry-level ($4K-$7K), mid-range ($7K-$10K), and pro-level ($10K-$14K) dirt bikes",
                    "Gear essentials: helmet, boots, goggles, gloves, and body armor — what to buy first as a new off-road rider"
                ]
            },
            {
                "title": "Cruiser Motorcycle Buying Guide: Harley vs Indian vs Japanese Alternatives",
                "category": "buying",
                "angle": "head-to-head comparison of cruiser brands and models",
                "key_points": [
                    "Harley-Davidson lineup overview: Street Bob, Low Rider, Road Glide — price, engine, and character of each",
                    "Indian Motorcycle comparison: Scout, Chief, Challenger — how Indian's PowerPlus engine and Ride Command tech stack up",
                    "Japanese cruiser alternatives: Honda Rebel 1100, Yamaha Eluder, Suzuki Boulevard — the value proposition with proven reliability",
                    "Price comparison across segments: entry ($7K-$10K), mid ($12K-$18K), and bagger/touring ($20K-$30K+)",
                    "Aftermarket and custom culture: which brand has the deepest parts ecosystem and strongest community"
                ]
            },
            {
                "title": "Sport Bike vs Naked Bike: Which Riding Position Fits Your Style and Daily Needs",
                "category": "reviews",
                "angle": "practical comparison of sport bike and naked bike ergonomics and real-world usability",
                "key_points": [
                    "Riding position breakdown: clip-on handlebars and rear sets on sport bikes vs upright bars on nakeds — comfort tested on long rides",
                    "Performance comparison: Yamaha R7 vs MT-07, Kawasaki ZX-6R vs Z900 — same engine platforms, very different characters",
                    "Wind protection: full fairing advantage at highway speeds vs naked bike buffeting and aftermarket windscreen options",
                    "Insurance cost difference: sport bikes typically 30-50% more expensive to insure than equivalent naked models",
                    "Versatility ranking: which naked bikes come with cruise control, quick shifters, and comfort seats for touring"
                ]
            },
            {
                "title": "Maxi Scooter Revolution: Why 500cc+ Scooters Are Taking Over City Commuting",
                "category": "reviews",
                "angle": "rise of maxi scooters and why they're replacing cars for urban transportation",
                "key_points": [
                    "Top maxi scooter models: Yamaha TMAX, BMW C 650 GT, Suzuki Burgman 650, Kymco AK 550 — specs and pricing compared",
                    "Practical advantages: built-in storage for two full-face helmets, low seat height, automatic CVT transmission, and weather protection",
                    "Highway capability: 500cc+ maxi scooters comfortably cruise at 75-80 mph with enough passing power for US freeways",
                    "Cost of ownership: fuel economy (50-65 mpg), insurance rates, tire life, and maintenance intervals vs a compact car",
                    "Who should buy one: urban commuters, riders with limited motorcycle experience, and those wanting motorcycle utility without manual shifting"
                ]
            },
            {
                "title": "Adventure Motorcycle Comparison: BMW GS vs KTM Adventure vs Ducati Multistrada",
                "category": "reviews",
                "angle": "flagship ADV face-off with real-world on and off-road testing",
                "key_points": [
                    "BMW R 1300 GS: the new benchmark with 145 hp, 12 kg weight reduction, and adaptive electronic suspension — starting at $20K",
                    "KTM 1290 Super Adventure R: the off-road focused champion with 160 hp, WP semi-active suspension, and 220mm ground clearance",
                    "Ducati Multistrada V4: 170 hp V4 Granturismo engine, radar-assisted cruise control, and 340-mile fuel range for touring",
                    "On-road ride quality and highway comfort comparison across all three with real rider feedback from a 500-mile road trip",
                    "Off-road capability: weight distribution, rider mode electronics, and tire options that determine which bike handles dirt best"
                ]
            },
            {
                "title": "Best Touring Motorcycles 2026: Cross-Country Comfort Machines for Long-Distance Riders",
                "category": "buying",
                "angle": "comprehensive touring bike guide with comfort, range, and cargo analysis",
                "key_points": [
                    "Top touring bikes ranked: Honda Gold Wing, Harley Road Glide, BMW K 1600 GT, Indian Challenger, and Yamaha Star Venture",
                    "Engine and ride quality: flat-six smoothness of Gold Wing vs inline-six power of K 1600 vs V-twin character of Harley and Indian",
                    "Infotainment and comfort features: Apple CarPlay, heated seats/grips, adjustable windshields, and premium audio systems",
                    "Luggage capacity comparison: factory hard bags capacity, top case options, and total cargo volume for multi-week trips",
                    "Long-term ownership: reliability records, service intervals, dealer network density, and resale value after 3 years and 30,000 miles"
                ]
            },
            {
                "title": "Cafe Racer Build Guide: How to Turn Any Motorcycle Into a Retro Custom on a Budget",
                "category": "maintenance",
                "angle": "step-by-step DIY guide for building a cafe racer from a donor bike",
                "key_points": [
                    "Choosing the right donor bike: Honda CB series, Yamaha XS650, BMW Airhead, Suzuki GS — what makes a good platform",
                    "Essential modifications: clip-on handlebars, rear-set foot pegs, seat cowl, and tail tidy for the classic cafe silhouette",
                    "Engine and exhaust upgrades: carburetor rebuild or EFI tune, aftermarket exhaust for the signature cafe racer sound",
                    "Paint and aesthetics: stripped-down look, classic racing colors, tank decals, and how to achieve the vintage patina",
                    "Budget breakdown: $500-$1,500 for entry-level build on a $1,000-$2,000 donor — realistic cost expectations for each phase"
                ]
            },
            {
                "title": "Best 125cc Motorcycles for City Commuting: Fuel-Efficient Urban Riders That Don't Sacrifice Style",
                "category": "buying",
                "angle": "buyer's guide to stylish and practical 125cc commuter motorcycles",
                "key_points": [
                    "Top 125cc models: Yamaha MT-125, Honda CB125R, KTM 125 Duke, Suzuki GSX-S125, and Aprilia RS 125 — specs and prices",
                    "Fuel economy and running costs: 100-130 mpg, cheap insurance, minimal maintenance, and annual cost of ownership under $1,000",
                    "Style and appearance: which 125s look like their bigger siblings and which have unique design language for the small-displacement class",
                    "Licensing advantage: 125cc bikes can be ridden with a basic motorcycle license in many states and most European countries",
                    "Urban practicality: lightweight (300-330 lbs), narrow profile for lane splitting, and sufficient speed for 45-55 mph city roads"
                ]
            },
            {
                "title": "Can-Am Ryker vs Harley-Davidson Tri Glide: Three-Wheel Motorcycle Comparison for 2026",
                "category": "reviews",
                "angle": "side-by-side comparison of the two most popular three-wheel motorcycles",
                "key_points": [
                    "Can-Am Ryker: 900cc Rotax triple engine, 82 hp, 2,000 rpm clutch engagement, starting at $16K — the sporty three-wheeler",
                    "Harley-Davidson Tri Glide Ultra: 1,868cc Milwaukee-Eight 114 V-twin, 90 hp, reverse gear, massive tour pack — starting at $33K",
                    "Riding dynamics comparison: leaning front end of Can-Am vs traditional two-wheel feel of Harley's rear axle setup",
                    "Practicality and storage: Ryker's front trunk vs Tri Glide's Tour-Pak and saddlebags — cargo capacity and touring readiness",
                    "Target buyer analysis: who should choose each — age, riding experience, budget, and intended use scenarios"
                ]
            },
            {
                "title": "Best Motorcycle for Tall Riders: 10 Bikes With Real Legroom That Actually Fit 6-Foot-Plus Riders",
                "category": "buying",
                "angle": "ergonomic buyer's guide for tall riders who struggle to fit on standard motorcycles",
                "key_points": [
                    "Seat height, peg position, and handlebar reach: the three key measurements that determine whether a bike fits tall riders",
                    "ADV bikes ranked for tall riders: KTM 890 Adventure (880mm seat), BMW R 1300 GS, Honda Africa Twin, and Tenere 700",
                    "Cruisers for tall riders: Indian Scout, Harley Street Glide, and BMW R 18 — forward controls and stretched wheelbases that help",
                    "Naked and standard options: Triumph Speed Twin 1200, Ducati Monster, and Suzuki GSX-S1000 with aftermarket peg lowering kits",
                    "Aftermarket solutions: peg lowering brackets, bar risers, gel seat modifications, and extended shift levers — $200-$500 for total ergonomic fix"
                ]
            },
        ],
    },
    "sub-food": {
        "brand": "FlavorFusion",
        "domain": "food.jycsd.com",
        "category": "Food & Cuisine",
        "brandColor": "amber-600",
        "brandHex": "#d97706",
        "fontHeading": "'Playfair Display', 'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#d97706",
        "blockquoteBg": "#fffbeb",
        "related_articles": [
            ("article-1.html", "Big Mac: The Iconic Burger That Defined American Fast Food"),
            ("article-2.html", "Mapo Tofu: Sichuan's Fiery Bean Curd That Numbs and Delights"),
            ("article-3.html", "French Onion Soup: The Timeless Bistro Classic with Melted Gruyère"),
        ],
        "custom_template": True,
        "tailwindColors": """brand: {50: '#fffbeb', 100: '#fef3c7', 200: '#fde68a', 400: '#fbbf24', 500: '#f59e0b', 600: '#d97706', 700: '#b45309', 800: '#92400e'}""",
        "predefined_topics": [
            # === Western Cuisine (21 articles) ===
            {"title": "Big Mac: The Iconic Burger That Defined American Fast Food", "category": "western"},
            {"title": "KFC Original Recipe Fried Chicken: The Colonel's Secret 11 Herbs and Spices", "category": "western"},
            {"title": "Pizza Hut Pan Pizza: The Story Behind America's Favorite Deep Dish", "category": "western"},
            {"title": "Whopper vs Big Mac: Burger King's Flame-Grilled Rivalry", "category": "western"},
            {"title": "Subway Italian BMT: Building the Perfect Custom Sandwich", "category": "western"},
            {"title": "Taco Bell Crunchwrap Supreme: Mexican-Inspired American Fast Food Innovation", "category": "western"},
            {"title": "French Onion Soup: The Timeless Bistro Classic with Melted Gruyère", "category": "western"},
            {"title": "Coq au Vin: Julia Child's French Country Chicken Braised in Red Wine", "category": "western"},
            {"title": "Croissant: The Buttery French Pastry That Conquered the World", "category": "western"},
            {"title": "Spaghetti Carbonara: Rome's Perfect Pasta with Just 5 Ingredients", "category": "western"},
            {"title": "Margherita Pizza: Naples' Gift to World Cuisine", "category": "western"},
            {"title": "Tiramisu: Italy's No-Bake Coffee Dream Dessert", "category": "western"},
            {"title": "Texas-Style BBQ Brisket: Low and Slow Smoked Beef Perfection", "category": "western"},
            {"title": "New England Lobster Roll: Buttery Seafood Bliss on a Toasted Bun", "category": "western"},
            {"title": "Classic American Cheeseburger: The Science Behind the Perfect Patty", "category": "western"},
            {"title": "Omurice: Japan's Beloved Western-Style Omelette Over Fried Rice", "category": "western"},
            {"title": "Japanese Curry Rice: How the British Navy Created Japan's Comfort Food", "category": "western"},
            {"title": "Tonkatsu: Japan's Crispy Pork Cutlet with Bulldog Sauce", "category": "western"},
            {"title": "Greek Moussaka: Layers of Eggplant, Meat, and Creamy Béchamel", "category": "western"},
            {"title": "Spanish Paella: Saffron-Infused Rice Dish from Valencia's Coast", "category": "western"},
            {"title": "Turkish Döner Kebab: The Rotating Meat That Changed Street Food Forever", "category": "western"},
            # === Chinese Cuisine - 8 Great Traditions (24 articles) ===
            {"title": "Mapo Tofu: Sichuan's Fiery Bean Curd That Numbs and Delights", "category_slug": "chinese"},
            {"title": "Kung Pao Chicken: The Sweet-Spicy-Savory Sichuan Stir-Fry Classic", "category_slug": "chinese"},
            {"title": "Shuizhu Yu: Sichuan Water-Boiled Fish in Fiery Chili Oil", "category_slug": "chinese"},
            {"title": "White Cut Chicken: Cantonese Poached Chicken with Ginger-Scallion Dip", "category_slug": "chinese"},
            {"title": "Char Siu: Cantonese Honey-Roasted BBQ Pork with Glossy Red Crust", "category_slug": "chinese"},
            {"title": "Har Gow: Crystal Shrimp Dumplings, the Dim Sum Crown Jewel", "category_slug": "chinese"},
            {"title": "Braised Sea Cucumber with Scallion: Shandong's Imperial Banquet Dish", "category_slug": "chinese"},
            {"title": "Sweet and Sour Carp: Shandong's Crispy Whole Fish Masterpiece", "category_slug": "chinese"},
            {"title": "Jiu Zhuan Da Chang: Shandong's Nine-Turn Braised Intestine", "category_slug": "chinese"},
            {"title": "Red Braised Pork Belly: Chairman Mao's Favorite Jiangsu Comfort Dish", "category_slug": "chinese"},
            {"title": "Squirrel-Shaped Mandarin Fish: Jiangsu's Sculptural Sweet-Sour Masterpiece", "category_slug": "chinese"},
            {"title": "Crab Meat Lion's Head: Jiangsu's Giant Pork Meatball in Broth", "category_slug": "chinese"},
            {"title": "Dongpo Pork: Zhejiang's Legendary Wine-Braised Pork Belly", "category_slug": "chinese"},
            {"title": "West Lake Vinegar Fish: Hangzhou's Sweet-Tart Freshwater Classic", "category_slug": "chinese"},
            {"title": "Longjing Shrimp: Zhejiang's Dragon Well Tea-Infused Stir-Fried Shrimp", "category_slug": "chinese"},
            {"title": "Buddha Jumps Over the Wall: Fujian's Legendary Luxurious Broth", "category_slug": "chinese"},
            {"title": "Lychee Pork: Fujian's Sweet-Sour Crispy Pork Resembling Lychee Fruit", "category_slug": "chinese"},
            {"title": "Oyster Omelette: Fujian's Crispy-Soft Street Food Classic", "category_slug": "chinese"},
            {"title": "Duojiao Yutou: Hunan Steamed Fish Head with Chopped Chili Peppers", "category_slug": "chinese"},
            {"title": "Xiaochao Rou: Hunan's Quick-Fried Pork with Chili and Fermented Black Beans", "category_slug": "chinese"},
            {"title": "Kou Wei Xia: Hunan's Spicy Crayfish Bursting with Chili and Garlic", "category_slug": "chinese"},
            {"title": "Stinky Mandarin Fish: Anhui's Fermented Fish That Tastes Better Than It Smells", "category_slug": "chinese"},
            {"title": "Mao Doufu: Anhui's Hairy Tofu, a Fermented Delicacy from the Mountains", "category_slug": "chinese"},
            {"title": "Li Hongzhang Chop Suey: Anhui's Legendary Official's Mixed Stew", "category_slug": "chinese"},
            # === Street Food (8 articles) ===
            {"title": "Jianbing: China's Ultimate Breakfast Crepe Made on a Griddle Cart", "category_slug": "street-food"},
            {"title": "Roujiamo: China's Ancient Meat Sandwich, the Original Burger", "category_slug": "street-food"},
            {"title": "New York Hot Dog: The Pushcart Sausage That Became an American Icon", "category_slug": "street-food"},
            {"title": "Mexican Tacos al Pastor: Spit-Roasted Pork on a Corn Tortilla", "category_slug": "street-food"},
            {"title": "Chinese Shengjian Bao: Shanghai's Pan-Fried Pork Soup Dumplings", "category_slug": "street-food"},
            {"title": "Fish and Chips: Britain's Crispy Deep-Fried Seaside Tradition", "category_slug": "street-food"},
            {"title": "Takoyaki: Osaka's Octopus-Filled Street Snack with Dancing Bonito Flakes", "category_slug": "street-food"},
            {"title": "Chuan'r: Beijing's Cumin-Spiced Lamb Skewers Over Charcoal Fire", "category_slug": "street-food"},
        ],
        "categories": [
            {"slug": "western", "name": "Western Cuisine", "desc": "From Michelin-starred restaurants to iconic fast food chains"},
            {"slug": "chinese", "name": "Chinese Cuisine", "desc": "Eight great culinary traditions across China's regions"},
            {"slug": "street-food", "name": "Street Food", "desc": "The world's best sidewalk eats from Beijing to New York"},
        ],
    },
    "rightsdaily": {
        "brand": "RightsDaily",
        "domain": "rightsdaily.com",
        "category": "Legal Rights",
        "brandColor": "blue-800",
        "brandHex": "#1e40af",
        "tailwindColors": """brand: {50: '#eff6ff', 100: '#dbeafe', 200: '#bfdbfe', 400: '#60a5fa', 500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8', 800: '#1e40af'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#3b82f6",
        "blockquoteBg": "#eff6ff",
        "related_articles": [
            ("article-1.html", "Know Your Rights: A Complete Guide to Consumer Protection Laws"),
            ("article-2.html", "Landlord-Tenant Disputes: Legal Options and Tenant Rights"),
            ("article-3.html", "Divorce Process Simplified: What You Need to Know Before Filing"),
        ],
    },
    "dailymedadvice": {
        "brand": "DailyMedAdvice",
        "domain": "dailymedadvice.com",
        "category": "Health & Medical",
        "brandColor": "green-700",
        "brandHex": "#15803d",
        "tailwindColors": """brand: {50: '#f0fdf4', 100: '#dcfce7', 200: '#bbf7d0', 400: '#4ade80', 500: '#22c55e', 600: '#16a34a', 700: '#15803d', 800: '#166534'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#22c55e",
        "blockquoteBg": "#f0fdf4",
        "related_articles": [
            ("article-1.html", "Understanding Common Cold vs Flu: Symptoms, Treatment, and When to See a Doctor"),
            ("article-2.html", "Blood Pressure 101: What Your Numbers Mean and How to Manage Them"),
            ("article-3.html", "Complete Guide to Vitamin D: Benefits, Sources, and Deficiency Symptoms"),
        ],
    },
    "entertainment": {
        "brand": "EntertainmentBuzz",
        "domain": "entertainment.jycsd.com",
        "category": "Entertainment",
        "brandColor": "purple-600",
        "brandHex": "#9333ea",
        "tailwindColors": """brand: {50: '#faf5ff', 100: '#f3e8ff', 200: '#e9d5ff', 400: '#c084fc', 500: '#a855f7', 600: '#9333ea', 700: '#7e22ce', 800: '#6b21a8'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#a855f7",
        "blockquoteBg": "#faf5ff",
        "related_articles": [
            ("article-1.html", "Celebrity News Roundup: Biggest Stories This Week You Missed"),
            ("article-2.html", "Top 10 Must-Watch TV Shows Premiering This Month"),
            ("article-3.html", "Hollywood Gossip: Behind-the-Scenes Secrets From Your Favorite Movies"),
        ],
    },
}

# HTML template skeleton with placeholders
TEMPLATE_SKELETON = """<!DOCTYPE html>
<html lang="en">
<head>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={{adsense_pub}}" crossorigin="anonymous"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id={{ga4_id}}"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', '{{ga4_id}}');
</script>
<meta charset="UTF-8">
<meta name="google-adsense-account" content="{{adsense_pub}}">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{{meta_tags}}
<meta name="robots" content="index, follow">
<meta property="og:site_name" content="{{brand}}">
<meta property="og:locale" content="en_US">
{{og_tags}}
<title>{{title}}</title>
<link rel="canonical" href="{{article_url}}">
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {
    theme: {
        extend: {
            colors: {
                {{tailwind_colors}}
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
                heading: [{{font_heading}}],
            }
        }
    }
}
</script>
<style>
.ad-unit {
    background: #f9fafb;
    border-radius: 8px;
    text-align: center;
    margin: 2.5rem 0;
    padding: 0.5rem 0 1.5rem 0;
    overflow: hidden;
}
.ad-label {
    display: block;
    text-align: center;
    font-size: 11px;
    color: #9ca3af;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.article-content h2 { font-size: 1.75rem; font-weight: 700; color: #111827; margin-top: 2.5rem; margin-bottom: 1rem; }
.article-content h3 { font-size: 1.35rem; font-weight: 600; color: #1f2937; margin-top: 2rem; margin-bottom: 0.75rem; }
.article-content p { margin-bottom: 1.25rem; line-height: 1.8; font-size: 1.1rem; color: #374151; }
.article-content ul, .article-content ol { margin-bottom: 1.25rem; padding-left: 1.5rem; }
.article-content li { margin-bottom: 0.5rem; line-height: 1.7; font-size: 1.05rem; color: #374151; }
.article-content blockquote {
    border-left: 4px solid {{blockquote_color}};
    padding: 1rem 1.5rem;
    margin: 2rem 0;
    background: {{blockquote_bg}};
    border-radius: 0 8px 8px 0;
    font-style: italic;
    color: #374151;
}
</style>
</head>
<body class="bg-white font-sans antialiased flex flex-col min-h-screen">
<header class="bg-white border-b border-gray-100 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
            <a href="index.html" class="text-2xl font-bold text-{{brand_color}} font-heading">{{brand}}</a>
            <nav class="hidden md:flex space-x-8 text-sm font-medium">
                <a href="index.html" class="text-gray-700 hover:text-{{brand_color}} transition">Home</a>
                <a href="about.html" class="text-gray-700 hover:text-{{brand_color}} transition">About</a>
                <a href="contact.html" class="text-gray-700 hover:text-{{brand_color}} transition">Contact</a>
            </nav>
        </div>
    </div>
</header>
<main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex-1">
    <nav class="text-sm text-gray-400 mb-8" aria-label="Breadcrumb">
        <a href="index.html" class="hover:text-{{brand_color}} transition">Home</a>
        <span class="mx-2">/</span>
        <span class="text-gray-600">{{breadcrumb}}</span>
    </nav>
    <article>
        <header class="mb-10">
            <h1 class="text-4xl md:text-5xl font-heading font-bold text-gray-900 leading-tight mb-4">{{h1_title}}</h1>
            <div class="flex items-center text-sm text-gray-400 space-x-4">
                <time datetime="{{date_iso}}">{{date_display}}</time>
                <span>{{read_time}} min read</span>
            </div>
        </header>
        {{cover_img_html}}
        <div class="article-content">
            {{article_body}}
        </div>
        <div class="mt-10 flex flex-wrap gap-2">
            {{tag_spans}}
        </div>
    </article>
    <aside class="mt-16 bg-gray-50 rounded-2xl p-8">
        <h3 class="text-lg font-bold text-gray-900 mb-6">Related Articles</h3>
        <div class="grid md:grid-cols-3 gap-6">
            <a href="{{related_1_url}}" class="block p-4 bg-white rounded-xl border border-gray-200 hover:border-{{brand_color}}/30 transition"><span class="text-sm text-{{brand_color}} font-medium">Related</span><p class="text-gray-700 text-sm mt-1">{{related_1_title}}</p></a>
            <a href="{{related_2_url}}" class="block p-4 bg-white rounded-xl border border-gray-200 hover:border-{{brand_color}}/30 transition"><span class="text-sm text-{{brand_color}} font-medium">Related</span><p class="text-gray-700 text-sm mt-1">{{related_2_title}}</p></a>
            <a href="{{related_3_url}}" class="block p-4 bg-white rounded-xl border border-gray-200 hover:border-{{brand_color}}/30 transition"><span class="text-sm text-{{brand_color}} font-medium">Related</span><p class="text-gray-700 text-sm mt-1">{{related_3_title}}</p></a>
        </div>
    </aside>
</main>
<footer class="bg-gray-900 text-gray-400 py-12 mt-auto">
    <div class="max-w-6xl mx-auto px-4">
        <div class="grid md:grid-cols-4 gap-8 mb-10">
            <div>
                <h3 class="text-white text-lg font-black mb-3">{{brand}}</h3>
                <p class="text-sm leading-relaxed">{{brand_description}}</p>
            </div>
            <div>
                <h4 class="text-white font-semibold mb-3">Legal</h4>
                <ul class="space-y-2 text-sm">
                    <li><a href="privacy-policy.html" class="hover:text-white transition-colors">Privacy Policy</a></li>
                    <li><a href="terms.html" class="hover:text-white transition-colors">Terms of Service</a></li>
                    <li><a href="cookie-policy.html" class="hover:text-white transition-colors">Cookie Policy</a></li>
                    <li><a href="contact.html" class="hover:text-white transition-colors">Contact</a></li>
                </ul>
            </div>
            <div>
                <h4 class="text-white font-semibold mb-3">Our Network</h4>
                <select onchange="if(this.value)window.location.href=this.value" class="w-full bg-gray-800 text-gray-300 text-sm rounded px-3 py-2 mb-3 border border-gray-700 focus:outline-none focus:border-{{brand_color}} cursor-pointer">
                    <option value="">-- Network --</option>
                    <option value="https://www.jycsd.com">Main Site</option>
                    <option value="https://games.jycsd.com">Game Guides</option>
                    <option value="https://anime.jycsd.com">Anime &amp; Manga</option>
                </select>
                <select onchange="if(this.value)window.location.href=this.value" class="w-full bg-gray-800 text-gray-300 text-sm rounded px-3 py-2 mb-3 border border-gray-700 focus:outline-none focus:border-{{brand_color}} cursor-pointer">
                    <option value="">-- Content Sites --</option>
                    <option value="https://healthy.jycsd.com">HealthyEats</option>
                    <option value="https://pets.jycsd.com">PetCare Hub</option>
                    <option value="https://home.jycsd.com">HomeJoy</option>
                    <option value="https://finance.jycsd.com">MoneyWise</option>
                    <option value="https://tech.jycsd.com">TechNest</option>
                    <option value="https://travel.jycsd.com">TripRoute</option>
                    <option value="https://auto.jycsd.com">AutoPulse</option>
                    <option value="https://moto.jycsd.com">MotoPulse</option>
                    <option value="https://food.jycsd.com">FlavorFusion</option>
                    <option value="https://rightsdaily.com">RightsDaily</option>
                    <option value="https://dailymedadvice.com">DailyMedAdvice</option>
                    <option value="https://entertainment.jycsd.com">PopCulture HQ</option>
                </select>
                <select onchange="if(this.value)window.location.href=this.value" class="w-full bg-gray-800 text-gray-300 text-sm rounded px-3 py-2 border border-gray-700 focus:outline-none focus:border-{{brand_color}} cursor-pointer">
                    <option value="">-- Game & Anime Wikis --</option>
                    <option value="https://dragonball.jycsd.com">Dragon Ball Wiki</option>
                    <option value="https://naruto.jycsd.com">Naruto Wiki</option>
                    <option value="https://onepiece.jycsd.com">One Piece Wiki</option>
                    <option value="https://valorant.jycsd.com">Valorant Wiki</option>
                    <option value="https://fortnite.jycsd.com">Fortnite Wiki</option>
                    <option value="https://lol.jycsd.com">LoL Wiki</option>
                    <option value="https://eldenring.jycsd.com">Elden Ring Wiki</option>
                    <option value="https://minecraft.jycsd.com">Minecraft Wiki</option>
                </select>
            </div>
            <div>
                <h4 class="text-white font-semibold mb-3">Contact</h4>
                <ul class="space-y-2 text-sm">
                    <li><a href="mailto:{{email}}" class="hover:text-white transition-colors">{{email}}</a></li>
                </ul>
            </div>
        </div>
        <div class="border-t border-gray-800 pt-6 text-center text-sm">
            <p>&copy; {{year}} {{brand}}. All rights reserved.</p>
        </div>
    </div>
</footer>
<script type="application/ld+json">
{{json_ld}}
</script>
</body>
</html>"""

def get_content_generation_prompt(site_dir, article_num, topic=None):
    """Returns just the content-relevant info for DeepSeek to generate the article body."""
    cfg = SITE_CONFIG[site_dir]
    domain = cfg["domain"]
    url = f"https://{domain}/article-{article_num}.html"
    today = datetime.now().strftime("%Y-%m-%d")
    result = {
        "brand": cfg["brand"],
        "category": cfg["category"],
        "domain": domain,
        "article_url": url,
        "article_num": article_num,
        "date": today,
        "brand_color": cfg["brandColor"],
        "brand_hex": cfg["brandHex"],
    }

    if topic:
        result["topic_title"] = topic["title"]
        result["topic_category"] = topic.get("category", topic.get("category_slug", ""))

    return result

FOOD_TEMPLATE_SKELETON = """<!DOCTYPE html>
<html lang="en">
<head>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={{adsense_pub}}" crossorigin="anonymous"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id={{ga4_id}}"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', '{{ga4_id}}');
</script>
<meta charset="UTF-8">
<meta name="google-adsense-account" content="{{adsense_pub}}">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{{meta_tags}}
<meta name="robots" content="index, follow">
<meta property="og:site_name" content="{{brand}}">
<meta property="og:locale" content="en_US">
{{og_tags}}
<title>{{title}}</title>
<link rel="canonical" href="{{article_url}}">
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {
    theme: {
        extend: {
            colors: {
                {{tailwind_colors}}
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
                heading: [{{font_heading}}],
            }
        }
    }
}
</script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Playfair+Display:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
.ad-unit {
    background: #f9fafb;
    border-radius: 8px;
    text-align: center;
    margin: 2.5rem 0;
    padding: 0.5rem 0 1.5rem 0;
    overflow: hidden;
}
.ad-label {
    display: block;
    text-align: center;
    font-size: 11px;
    color: #9ca3af;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
blockquote {
    border-left: 4px solid {{blockquote_color}};
    background: {{blockquote_bg}};
    padding: 1rem 1.5rem;
    margin: 1.5rem 0;
    border-radius: 0 8px 8px 0;
    font-style: italic;
}
.recipe-meta-icon {
    width: 20px; height: 20px;
    display: inline-block;
}
</style>
</head>
<body class="bg-stone-50 text-gray-800 font-sans flex flex-col min-h-screen">

<!-- Nav -->
<nav class="bg-white/95 backdrop-blur-sm sticky top-0 z-50 border-b border-amber-100">
    <div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <a href="index.html" class="text-2xl font-black text-gray-900 tracking-tight font-heading">
            Flavor<span class="text-brand-600">Fusion</span>
        </a>
        <div class="hidden md:flex items-center gap-8 text-sm font-medium">
            <a href="index.html" class="text-gray-600 hover:text-brand-600 transition-colors">Home</a>
            <a href="category-western.html" class="text-gray-600 hover:text-brand-600 transition-colors">Western Cuisine</a>
            <a href="category-chinese.html" class="text-gray-600 hover:text-brand-600 transition-colors">Chinese Cuisine</a>
            <a href="category-street-food.html" class="text-gray-600 hover:text-brand-600 transition-colors">Street Food</a>
            <a href="about.html" class="text-gray-600 hover:text-brand-600 transition-colors">About</a>
            <a href="contact.html" class="text-gray-600 hover:text-brand-600 transition-colors">Contact</a>
        </div>
        <button class="md:hidden text-gray-600 text-2xl">&amp;#9776;</button>
    </div>
</nav>

<main class="flex-1">
    <!-- Recipe Hero -->
    <section class="relative h-[30vh] md:h-[35vh] bg-gray-300 overflow-hidden">
        {{cover_img_html}}
        <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent"></div>
        <div class="absolute bottom-0 left-0 right-0 p-6 md:p-12 max-w-4xl mx-auto">
            <div class="flex flex-wrap gap-2 mb-3">{{tag_spans}}</div>
            <h1 class="text-3xl md:text-4xl lg:text-5xl font-black text-white font-heading leading-tight">{{h1_title}}</h1>
        </div>
    </section>

    <!-- Recipe Metadata Bar -->
    <div class="max-w-4xl mx-auto px-4 -mt-10 relative z-10">
        <div class="bg-white rounded-2xl shadow-lg p-5 md:p-6 flex flex-wrap justify-center gap-6 md:gap-10 text-center">
            <div class="flex flex-col items-center">
                <svg class="w-6 h-6 text-brand-600 mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                <span class="text-xs text-gray-500 uppercase tracking-wide">Prep Time</span>
                <span class="text-sm font-semibold text-gray-900">{{prep_time}}</span>
            </div>
            <div class="flex flex-col items-center">
                <svg class="w-6 h-6 text-brand-600 mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"/></svg>
                <span class="text-xs text-gray-500 uppercase tracking-wide">Cook Time</span>
                <span class="text-sm font-semibold text-gray-900">{{cook_time}}</span>
            </div>
            <div class="flex flex-col items-center">
                <svg class="w-6 h-6 text-brand-600 mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                <span class="text-xs text-gray-500 uppercase tracking-wide">Servings</span>
                <span class="text-sm font-semibold text-gray-900">{{servings}}</span>
            </div>
            <div class="flex flex-col items-center">
                <svg class="w-6 h-6 text-brand-600 mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                <span class="text-xs text-gray-500 uppercase tracking-wide">Difficulty</span>
                <span class="text-sm font-semibold text-gray-900">{{difficulty}}</span>
            </div>
        </div>
    </div>

    <!-- Article Content -->
    <article class="max-w-6xl mx-auto px-4 py-10">
        <div class="flex flex-col lg:flex-row gap-8">
            <!-- Main Content -->
            <div class="flex-1 min-w-0">
                <div class="bg-white rounded-2xl shadow-sm p-6 md:p-10">
                    <div class="flex items-center gap-3 text-sm text-gray-500 mb-8 pb-6 border-b border-gray-100">
                        <span>{{date_display}}</span>
                        <span>&middot;</span>
                        <span>{{read_time}} min read</span>
                    </div>
                    <div class="prose prose-lg max-w-none prose-headings:font-heading prose-headings:text-gray-900 prose-p:text-gray-600 prose-p:leading-relaxed prose-li:text-gray-600 prose-a:text-brand-600">
                        {{article_body}}
                    </div>
                </div>

                <!-- Tags -->
                <div class="flex flex-wrap gap-2 mt-6">{{tag_spans}}</div>
            </div>

            <!-- Sidebar -->
            <aside class="lg:w-72 flex-shrink-0">
                <div class="sticky top-24 space-y-6">

                    <!-- Related Recipes -->
                    <div class="bg-white rounded-2xl shadow-sm p-6">
                        <h3 class="font-bold text-gray-900 mb-4 font-heading text-lg">Related Recipes</h3>
                        <div class="space-y-3">
                            <a href="{{related_1_url}}" class="block p-3 bg-gray-50 rounded-xl hover:bg-brand-50 transition"><span class="text-xs text-brand-600 font-medium">Related</span><p class="text-gray-700 text-sm mt-1">{{related_1_title}}</p></a>
                            <a href="{{related_2_url}}" class="block p-3 bg-gray-50 rounded-xl hover:bg-brand-50 transition"><span class="text-xs text-brand-600 font-medium">Related</span><p class="text-gray-700 text-sm mt-1">{{related_2_title}}</p></a>
                            <a href="{{related_3_url}}" class="block p-3 bg-gray-50 rounded-xl hover:bg-brand-50 transition"><span class="text-xs text-brand-600 font-medium">Related</span><p class="text-gray-700 text-sm mt-1">{{related_3_title}}</p></a>
                        </div>
                    </div>
                </div>
            </aside>
        </div>
    </article>
</main>

<!-- Footer -->
<footer class="bg-gray-900 text-gray-400 py-12 mt-auto">
    <div class="max-w-6xl mx-auto px-4">
        <div class="grid md:grid-cols-4 gap-8 mb-10">
            <div>
                <h3 class="text-white text-lg font-black mb-3 font-heading">Flavor<span class="text-brand-500">Fusion</span></h3>
                <p class="text-sm leading-relaxed">Where East meets West — authentic recipes from both sides of the world.</p>
            </div>
            <div>
                <h4 class="text-white font-semibold mb-3">Legal</h4>
                <ul class="space-y-2 text-sm">
                    <li><a href="privacy-policy.html" class="hover:text-white transition-colors">Privacy Policy</a></li>
                    <li><a href="terms.html" class="hover:text-white transition-colors">Terms of Service</a></li>
                    <li><a href="cookie-policy.html" class="hover:text-white transition-colors">Cookie Policy</a></li>
                    <li><a href="contact.html" class="hover:text-white transition-colors">Contact</a></li>
                </ul>
            </div>
            <div>
                <h4 class="text-white font-semibold mb-3">Our Network</h4>
                <select onchange="if(this.value)window.location.href=this.value" class="w-full bg-gray-800 text-gray-300 text-sm rounded px-3 py-2 mb-3 border border-gray-700 focus:outline-none focus:border-indigo-500 cursor-pointer">
                    <option value="">— Network —</option>
                    <option value="https://www.jycsd.com">Main Site</option>
                    <option value="https://games.jycsd.com">Game Guides</option>
                    <option value="https://anime.jycsd.com">Anime &amp; Manga</option>
                </select>
                <select onchange="if(this.value)window.location.href=this.value" class="w-full bg-gray-800 text-gray-300 text-sm rounded px-3 py-2 mb-3 border border-gray-700 focus:outline-none focus:border-indigo-500 cursor-pointer">
                    <option value="">-- Content Sites --</option>
                    <option value="https://healthy.jycsd.com">HealthyEats</option>
                    <option value="https://pets.jycsd.com">PetCare Hub</option>
                    <option value="https://home.jycsd.com">HomeJoy</option>
                    <option value="https://finance.jycsd.com">MoneyWise</option>
                    <option value="https://tech.jycsd.com">TechNest</option>
                    <option value="https://travel.jycsd.com">TripRoute</option>
                    <option value="https://auto.jycsd.com">AutoPulse</option>
                    <option value="https://moto.jycsd.com">MotoPulse</option>
                    <option value="https://rightsdaily.com">RightsDaily</option>
                    <option value="https://dailymedadvice.com">DailyMedAdvice</option>
                    <option value="https://entertainment.jycsd.com">PopCulture HQ</option>
                    <option value="https://food.jycsd.com">FlavorFusion</option>
                </select>
                <select onchange="if(this.value)window.location.href=this.value" class="w-full bg-gray-800 text-gray-300 text-sm rounded px-3 py-2 border border-gray-700 focus:outline-none focus:border-indigo-500 cursor-pointer">
                    <option value="">-- Game & Anime Wikis --</option>
                    <option value="https://dragonball.jycsd.com">Dragon Ball Wiki</option>
                    <option value="https://naruto.jycsd.com">Naruto Wiki</option>
                    <option value="https://onepiece.jycsd.com">One Piece Wiki</option>
                    <option value="https://valorant.jycsd.com">Valorant Wiki</option>
                    <option value="https://fortnite.jycsd.com">Fortnite Wiki</option>
                    <option value="https://lol.jycsd.com">LoL Wiki</option>
                    <option value="https://eldenring.jycsd.com">Elden Ring Wiki</option>
                    <option value="https://minecraft.jycsd.com">Minecraft Wiki</option>
                </select>
            </div>
            <div>
                <h4 class="text-white font-semibold mb-3">Contact</h4>
                <ul class="space-y-2 text-sm">
                    <li><a href="mailto:contact@jycsd.com" class="hover:text-white transition-colors">contact@jycsd.com</a></li>
                </ul>
            </div>
        </div>
        <div class="border-t border-gray-800 pt-6 text-center text-sm">
            <p>&copy; 2020-2026 FlavorFusion. All rights reserved.</p>
        </div>
    </div>
    <div class="text-center text-sm mt-4"><a href="https://jycsd.com" class="hover:text-slate-600 transition-colors">Visit jycsd.com for more guides</a></div>
</footer>
</body>
</html>"""

def render_article_html(site_dir, ai_output):
    """Inject AI-generated content into the site template. ai_output is a dict with keys:
    title, description, keywords, og_title, og_description,
    h1_title, breadcrumb, cover_img_html, article_body_html,
    tag_spans, json_ld, read_time, date_iso, date_display
    """
    cfg = SITE_CONFIG[site_dir]
    vars_dict = {**GLOBALS, **cfg}

    # Generate meta tags server-side (AI never includes these — don't rely on it)
    description = ai_output.get("description", ai_output["h1_title"])
    desc_clean = description.replace('"', "&quot;").replace("\n", " ")
    article_url = ai_output.get("article_url", f"https://{cfg['domain']}/article-N.html")
    og_title = ai_output.get("og_title", ai_output["title"])
    og_title_clean = og_title.replace('"', "&quot;")
    vars_dict["meta_tags"] = f'<meta name="description" content="{desc_clean}">'
    vars_dict["og_tags"] = (
        f'<meta property="og:description" content="{desc_clean}">\n'
        f'    <meta property="og:title" content="{og_title_clean}">\n'
        f'    <meta property="og:url" content="{article_url}">\n'
        f'    <meta property="og:type" content="article">'
    )
    # Avoid brand duplication: if AI title already includes brand name, don't append it
    title = ai_output["title"]
    brand_name = cfg.get("brand", "")
    if brand_name and brand_name not in title:
        title = f"{title} - {brand_name}"
    vars_dict["title"] = title
    vars_dict["article_url"] = article_url
    vars_dict["h1_title"] = ai_output["h1_title"]
    vars_dict["breadcrumb"] = ai_output.get("breadcrumb", ai_output["h1_title"])
    vars_dict["article_body"] = ai_output["article_body_html"]
    vars_dict["tag_spans"] = ai_output.get("tag_spans", "")
    vars_dict["json_ld"] = ai_output["json_ld"]
    vars_dict["read_time"] = ai_output.get("read_time", "7")
    vars_dict["date_iso"] = ai_output["date_iso"]
    vars_dict["date_display"] = ai_output["date_display"]
    # Cover image (optional, generated by Seedream pipeline)
    image_url = ai_output.get("cover_img_url", "")
    if image_url:
        vars_dict["cover_img_html"] = f'<img src="{image_url}" alt="{ai_output.get("h1_title", "")}" class="w-full rounded-2xl mb-10" loading="lazy">'
        og_image_url = f"https://{cfg['domain']}/{image_url}"
    else:
        vars_dict["cover_img_html"] = ""
        # Default OG image fallback
        og_image_url = f"https://{cfg['domain']}/images/default-og.jpg"
    vars_dict["og_tags"] += f'\n    <meta property="og:image" content="{og_image_url}">'
    vars_dict["brand_color"] = cfg["brandColor"]
    vars_dict["tailwind_colors"] = cfg["tailwindColors"]
    vars_dict["font_heading"] = cfg["fontHeading"]
    vars_dict["blockquote_color"] = cfg["blockquoteColor"]
    vars_dict["blockquote_bg"] = cfg["blockquoteBg"]
    vars_dict["brand_description"] = cfg.get("brand_description", f"{cfg['brand']} provides practical information for everyday life.")

    # Default recipe metadata (only used by food template)
    vars_dict["prep_time"] = ai_output.get("prep_time", "15 mins")
    vars_dict["cook_time"] = ai_output.get("cook_time", "30 mins")
    vars_dict["servings"] = ai_output.get("servings", "4")
    vars_dict["difficulty"] = ai_output.get("difficulty", "Medium")

    # Network section — single link back to hub only (no PBN cross-linking)
    vars_dict["network_section"] = """<div class="text-center mb-6">
                <p class="text-sm text-gray-400">Part of the <a href="https://www.jycsd.com" class="text-{{brand_color}} hover:underline transition">Myers Media</a> network.</p>
            </div>"""

    # Dynamic related articles — scan site for actual article files
    site_path = ROOT / site_dir
    article_files = sorted(site_path.glob("article-*.html"))
    related_data = []
    for af in article_files:
        try:
            content = af.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"<title>(.*?)</title>", content)
            title = m.group(1) if m else af.stem.replace("-", " ").title()
            # Remove brand suffix (e.g., " - BrandName")
            title = re.sub(r"\s*[-–|]\s*\S.*$", "", title).strip()
            related_data.append((af.name, title))
        except Exception:
            pass
    random.shuffle(related_data)
    selected = related_data[:3]
    # Fill missing slots with link to articles listing
    while len(selected) < 3:
        selected.append(("articles.html", "Browse More Articles"))
    vars_dict["related_1_url"] = selected[0][0]
    vars_dict["related_1_title"] = selected[0][1]
    vars_dict["related_2_url"] = selected[1][0]
    vars_dict["related_2_title"] = selected[1][1]
    vars_dict["related_3_url"] = selected[2][0]
    vars_dict["related_3_title"] = selected[2][1]

    template = FOOD_TEMPLATE_SKELETON if cfg.get("custom_template") else TEMPLATE_SKELETON
    html = template
    for key, value in vars_dict.items():
        html = html.replace("{{" + key + "}}", str(value))

    return html, vars_dict

def quick_validate(html, site_dir):
    """Fast validation of rendered HTML."""
    issues = []
    cfg = SITE_CONFIG[site_dir]
    domain = cfg["domain"]
    if not html.startswith("<!DOCTYPE html>"):
        issues.append("Missing DOCTYPE")
    if "source.unsplash.com" in html:
        issues.append("Dead source.unsplash.com URL")
    if "30330238@qq.com" in html:
        issues.append("QQ email leaked through")
    if GLOBALS["ga4_id"] not in html:
        issues.append("Missing GA4 tag")
    if GLOBALS["adsense_pub"] not in html:
        issues.append("Missing AdSense pub ID")
    if domain not in html:
        issues.append("Wrong domain")
    # og:image must use the site's own domain, never external
    import re
    ogm = re.search(r'<meta\s+property="og:image"\s+content="([^"]*)"', html)
    if ogm:
        og_url = ogm.group(1)
        if "unsplash" in og_url or "images.unsplash" in og_url:
            issues.append(f"og:image uses unsplash external URL: {og_url}")
        elif "pexels" in og_url or "pixabay" in og_url:
            issues.append(f"og:image uses external stock photo: {og_url}")
        elif f"https://{domain}/" not in og_url:
            issues.append(f"og:image domain mismatch: {og_url} (expected https://{domain}/...)")
    else:
        issues.append("Missing og:image")
    return issues
