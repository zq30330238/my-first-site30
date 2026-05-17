"""Article-to-category mapping + category page metadata for 4 sub-sites."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CATEGORIES = {
    "sub-healthy": {
        "Recipes": {
            "slug": "recipes",
            "title": "Healthy Recipes & Smoothies",
            "desc": "Quick, delicious, and nutritious recipes for every meal of the day.",
            "hero_title": "Healthy Recipes",
            "hero_subtitle": "Quick, delicious, and nutritious recipes for every meal.",
            "articles": [6, 21],
        },
        "Nutrition": {
            "slug": "nutrition",
            "title": "Nutrition Science & Guides",
            "desc": "Evidence-based nutrition advice to help you make smarter food choices.",
            "hero_title": "Nutrition Guide",
            "hero_subtitle": "Science-backed advice for smarter food choices.",
            "articles": [1,4,5,8,9,10,12,13,14,15,16,17,18,20,23,25,26,27,28,30,31,32],
        },
        "Meal Plans": {
            "slug": "meal-plans",
            "title": "Meal Plans & Healthy Eating Strategies",
            "desc": "Practical meal planning guides to save time, money, and eat healthier.",
            "hero_title": "Meal Plans",
            "hero_subtitle": "Practical strategies to plan, prep, and eat healthier every week.",
            "articles": [2,3,7,11,19,22],
        },
    },
    "sub-pets": {
        "Dogs": {
            "slug": "dogs",
            "title": "Dog Care Guides — Nutrition, Training & Health",
            "desc": "Expert advice on dog nutrition, training, health, and everyday care.",
            "hero_title": "Dog Care",
            "hero_subtitle": "Nutrition, training, and health guides for happy, healthy dogs.",
            "articles": [1,3,4,5,7,8,10,11,13,14,18,19,20,23,25],
        },
        "Cats": {
            "slug": "cats",
            "title": "Cat Care Guides — Behavior, Health & Training",
            "desc": "Everything you need to know about cat behavior, health, and care.",
            "hero_title": "Cat Care",
            "hero_subtitle": "Behavior, health, and care guides for contented cats.",
            "articles": [2,9,12,15,16,17,24,30,32],
        },
        "Small Pets": {
            "slug": "small-pets",
            "title": "Small Pet Care — Rabbits, Birds, Fish & More",
            "desc": "Complete care guides for rabbits, hamsters, birds, fish, and other small pets.",
            "hero_title": "Small Pet Care",
            "hero_subtitle": "Care guides for rabbits, birds, fish, hamsters, and more.",
            "articles": [6,21,27,28,31,33],
        },
    },
    "sub-tech": {
        "Reviews": {
            "slug": "reviews",
            "title": "Tech Reviews — Honest Product Comparisons",
            "desc": "In-depth, unbiased reviews of smartphones, laptops, headphones, and more.",
            "hero_title": "Tech Reviews",
            "hero_subtitle": "Honest, in-depth reviews to help you buy smarter.",
            "articles": [1,5,7,10,13,14,19,22,25,27,30,32,33,38,39],
        },
        "Guides": {
            "slug": "guides",
            "title": "Tech Guides — Setup, Optimization & How-To",
            "desc": "Step-by-step guides for home office, gaming PCs, networking, and more.",
            "hero_title": "Tech Guides",
            "hero_subtitle": "Step-by-step tutorials for setup, optimization, and troubleshooting.",
            "articles": [2,6,8,11,12,15,18,21,26,28,31,35,37],
        },
        "AI": {
            "slug": "ai",
            "title": "AI Tools & Artificial Intelligence",
            "desc": "Explore AI tools that transform your workflow and daily productivity.",
            "hero_title": "AI & Automation",
            "hero_subtitle": "Discover AI tools that supercharge your workflow.",
            "articles": [3],
        },
        "Security": {
            "slug": "security",
            "title": "Cybersecurity & Online Privacy Guides",
            "desc": "Protect yourself online with practical cybersecurity and privacy guides.",
            "hero_title": "Security & Privacy",
            "hero_subtitle": "Protect your digital life with practical security guides.",
            "articles": [4,9,16,17,20,23,24,29,36],
        },
    },
    "sub-travel": {
        "Budget Travel": {
            "slug": "budget-travel",
            "title": "Budget Travel — Save Money on Every Trip",
            "desc": "Proven strategies to find cheap flights, accommodations, and travel deals.",
            "hero_title": "Budget Travel",
            "hero_subtitle": "Save money on flights, hotels, and every aspect of your trip.",
            "articles": [2,7,8,12,13,14,15,18,25,28,31,33,34,37],
        },
        "Destinations": {
            "slug": "destinations",
            "title": "Travel Destinations — Where to Go Next",
            "desc": "In-depth destination guides with budget tips for every region.",
            "hero_title": "Destinations",
            "hero_subtitle": "Discover your next adventure with in-depth destination guides.",
            "articles": [1,9,24,35,36],
        },
        "Tips": {
            "slug": "tips",
            "title": "Travel Tips — Packing, Safety & Smart Travel",
            "desc": "Practical travel advice from packing light to staying safe abroad.",
            "hero_title": "Travel Tips",
            "hero_subtitle": "Packing, safety, and smart travel advice for every journey.",
            "articles": [3,4,5,10,11,16,17,20,21,22,26,27,29,30,32],
        },
        "Digital Nomad": {
            "slug": "digital-nomad",
            "title": "Digital Nomad — Work From Anywhere",
            "desc": "Guides for remote workers: best destinations, gear, and lifestyle tips.",
            "hero_title": "Digital Nomad",
            "hero_subtitle": "Work from anywhere with our remote lifestyle guides.",
            "articles": [6,23],
        },
    },
}
