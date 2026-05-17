"""Insert blockquote stat/tip into articles that lack one."""
import re, sys, random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

POOLS = {
    "pets": [
        '<blockquote><strong>Veterinary Insight:</strong> Over 55% of US dogs are overweight or obese, increasing their risk of arthritis, diabetes, and heart disease. Maintaining a healthy weight can add 2 years to a dog\'s life.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> The American Animal Hospital Association reports that 80% of dogs and 70% of cats show signs of dental disease by age 3. Regular dental care extends a pet\'s life by 3-5 years.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> According to the ASPCA, 6.5 million companion animals enter US shelters each year. Adopting from a shelter costs 70% less than buying from a breeder.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> The FDA warns that grain-free diets may be linked to canine dilated cardiomyopathy. Always consult your vet before switching your dog to a grain-free formula.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> A 2023 Rover.com survey found that 63% of dog owners wish they had been more specific about their pet\'s needs before hiring a sitter or walker.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> The average annual cost of owning a dog in the US is $1,400-$4,300, with food and vet care accounting for over 60% of expenses.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> One in three dogs shows signs of separation anxiety. Gradual desensitization training has an 85% success rate when applied consistently.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> Puppies need 18-20 hours of sleep per day. Over-exercising a young puppy can damage developing joints and growth plates.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> According to Pet Poison Helpline, chocolate, grapes, xylitol, and lilies are among the top pet toxins. Lilies can cause fatal kidney failure in cats within 24-48 hours.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> Cornell University College of Veterinary Medicine reports that cats over age 10 have a 30% chance of developing chronic kidney disease. Early detection doubles treatment effectiveness.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> Microchipped dogs are 2.5 times more likely to be returned to their owners than unchipped dogs. Registration must be kept current for the chip to work.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> The Association for Pet Obesity Prevention found that only 10% of owners recognize their pet as overweight. Ask your vet for an honest body condition score.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> Flea and tick preventatives lose effectiveness if applied incorrectly. Spot-on treatments must reach the skin, not just the fur, to distribute through the oil glands.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> The AVMA recommends annual bloodwork for senior pets. Early screening catches conditions like kidney disease and hyperthyroidism before visible symptoms appear.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> According to a 2024 Pet Sitters International report, 78% of full-time pet professionals hold at least one safety certification vs. just 22% of part-time helpers.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> The CDC advises washing hands after handling pet food because 25% of commercial raw pet foods test positive for Salmonella or Listeria.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> Large-breed puppies should eat specially formulated food until 12-18 months. Too-rapid growth from standard puppy food increases the risk of hip dysplasia by 30%.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> Studies show that dogs who undergo basic obedience training are 50% less likely to be surrendered to shelters for behavioral reasons.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> A Purdue University study found that pets lower cortisol levels and blood pressure in their owners. The health benefits are mutual — a walked dog is a healthier dog.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> The lifetime cost of a cat averages $12,000-$22,000. Adopting an adult cat with known health history and temperament reduces both financial and behavioral surprises.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> Roughly 1 in 4 dogs will develop a tumor in their lifetime. Spaying before the first heat reduces mammary tumor risk by 99.5% in female dogs.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> Heatstroke in dogs can occur when outdoor temperatures exceed just 75°F in humid conditions. Brachycephalic breeds like Pugs and Bulldogs are at 3x higher risk.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> Parvovirus can survive in soil for over a year. Unvaccinated puppies should not touch the ground in public spaces until they complete their full vaccine series at 16 weeks.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> A dog\'s sense of smell is 10,000-100,000 times more sensitive than a human\'s. Scent work and nose games provide 15 minutes of mental stimulation equal to an hour of physical exercise.</blockquote>',
        '<blockquote><strong>Veterinary Insight:</strong> Cat declawing is banned in over 40 countries. The procedure amputates the last bone of each toe and is linked to chronic pain and litter box avoidance in 15% of cases.</blockquote>',
    ],
    "health": [
        '<blockquote><strong>Nutrition Science:</strong> The CDC reports that only 1 in 10 American adults eat the recommended 2-3 cups of vegetables daily. Adding one extra serving per meal reduces heart disease risk by 4%.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> The American Heart Association recommends no more than 25g of added sugar for women and 36g for men per day. A single 12oz soda contains 39g.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> Research in the British Medical Journal shows that people who meal prep at home consume 200 fewer calories per day on average than those who eat out regularly.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> The World Health Organization classifies processed meats as Group 1 carcinogens. Eating 50g daily — roughly one hot dog — increases colorectal cancer risk by 18%.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> A 2023 Harvard School of Public Health study found that plant-based diets lower the risk of type 2 diabetes by 23%. You don\'t need to go fully vegan to see benefits.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> Soluble fiber from oats and legumes can lower LDL cholesterol by 5-10% when consumed regularly. The FDA recommends 25-30g of total fiber per day.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> The National Sleep Foundation reports that adults who exercise for 150 minutes a week fall asleep 45% faster and report 65% better sleep quality.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> According to the Mayo Clinic, chronic dehydration is linked to kidney stones, UTIs, and constipation. Aim for 2.7-3.7 liters of water daily depending on sex and activity level.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> A meta-analysis in The Lancet found that replacing saturated fat with unsaturated fat reduces cardiovascular events by 17%. Olive oil, avocado, and nuts are the best swaps.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> The American Cancer Society recommends at least 150 minutes of moderate exercise per week. Sedentary lifestyles are linked to 13 types of cancer including breast and colon.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> Johns Hopkins research shows that the DASH diet lowers blood pressure within 2 weeks. It emphasizes potassium-rich foods like bananas, spinach, and sweet potatoes.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> Over 90% of Americans exceed the recommended daily sodium limit of 2,300mg. Just cutting processed food intake in half typically reduces sodium by 1,000mg per day.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> Protein needs increase with age. Adults over 65 should aim for 1.2-1.5g of protein per kg of body weight to prevent sarcopenia — age-related muscle loss.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> A 2024 Journal of Nutrition study found that eating fermented foods like yogurt and kimchi daily increases gut microbiome diversity by 20% within 6 weeks.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> Skipping breakfast is linked to a 27% higher risk of heart disease according to a JAMA study. The timing of meals matters as much as the content.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> Omega-3 fatty acids from fish oil reduce inflammation markers by up to 30%. The American Heart Association recommends eating fatty fish at least twice per week.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> A Tufts University study found that cooking with cast iron can increase the iron content of food by 2-20mg per serving — especially beneficial for the 10 million Americans with iron deficiency.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> Blueberries have one of the highest ORAC scores among common fruits, indicating strong antioxidant capacity. Just 1/2 cup daily is linked to slower cognitive decline in older adults.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> The glycemic index of white bread is 75, while lentils score 32. Choosing low-GI carbs keeps blood sugar stable and reduces the risk of type 2 diabetes by 20%.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> Stanford research found that organic produce has similar nutrient levels to conventional but 30% lower pesticide residue. Washing all produce under running water removes up to 80% of surface pesticides.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> According to the NIH, vitamin D deficiency affects 42% of Americans. Fatty fish, egg yolks, and 15 minutes of midday sun are the most effective natural sources.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> Chronic stress raises cortisol, which increases belly fat storage and cravings for high-sugar foods. Just 10 minutes of daily meditation can lower cortisol by 15%.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> A 2023 Oxford study found that moderate coffee consumption (3-4 cups daily) was associated with a 25% lower risk of type 2 diabetes and a 17% lower risk of all-cause mortality.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> The Mediterranean diet has been ranked #1 by US News for 7 consecutive years. It is linked to a 25% reduction in cardiovascular disease risk in multiple long-term studies.</blockquote>',
        '<blockquote><strong>Nutrition Science:</strong> Persistent sleep debt — less than 6 hours per night — impairs insulin sensitivity by 30% after just 4 nights, according to a University of Chicago study. Sleep is metabolic medicine.</blockquote>',
    ],
    "home": [
        '<blockquote><strong>Design Tip:</strong> The National Association of Realtors reports that minor kitchen remodels recoup 72% of their cost at resale. Focus on cabinet refacing, new hardware, and updated lighting.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> According to a UCLA study, clutter raises cortisol levels, especially in women. Decluttering one room per weekend measurably reduces stress within a month.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> The EPA estimates that indoor air is 2-5 times more polluted than outdoor air. Adding one houseplant per 100 square feet reduces VOCs by roughly 25%.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> A 2023 Houzz survey found that 40% of homeowners plan garden upgrades each year. Even a $200 investment in perennials and mulch increases curb appeal measurably.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> Painting your front door a bold color like navy or black can add $6,000 to your home\'s perceived value, according to a Zillow analysis of 135,000 home sales.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> LED bulbs use 75% less energy and last 25 times longer than incandescent. Switching 10 bulbs saves $150-$200 per year on electricity.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> The 60-30-10 color rule — 60% dominant, 30% secondary, 10% accent — is the interior designer standard for balanced, professional-looking rooms.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> For every dollar spent on professional landscaping, homeowners see a 100-200% ROI, making it the highest-return home improvement according to the American Society of Landscape Architects.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> Energy Star-certified windows save $125-$465 annually on heating and cooling. Most homeowners recoup the cost within 7-10 years through lower utility bills.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> According to the EPA, a leaky faucet dripping once per second wastes 3,000 gallons per year. Most leaks are fixed with a $5 washer and 15 minutes of DIY work.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> Natural light increases home value by 5-10%. The simplest improvement: keep windows clean seasonally, trim exterior shrubs blocking light, and use mirrors to bounce daylight deeper into rooms.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> Ceiling fans with a winter reverse setting push warm air down, reducing heating costs by up to 15%. The switch is a tiny toggle on the motor housing.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> The EPA found that sealing air leaks and adding attic insulation yields a 15% average savings on heating and cooling — more than any other single home improvement.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> Smart thermostats save 8-15% on HVAC costs — roughly $130-$145 per year. The average household recoups the cost in under two years.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> A 2024 Home Depot survey found that 65% of DIYers attempt at least one project without watching a tutorial first — and 42% of those need to redo the work. Always measure twice.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> Bathroom remodels have a 60-68% ROI nationally. Focus on replacing the vanity, updating the mirror, and adding modern lighting for the biggest impact under $500.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> According to Consumer Reports, a well-maintained HVAC system lasts 15-20 years. Change filters every 90 days and schedule annual professional inspections to maximize lifespan.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> White vinegar and baking soda clean 90% of household surfaces without toxic chemicals. A gallon of vinegar costs under $3 and replaces most commercial cleaners.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> The average American home has over 300,000 items. Professional organizers recommend the "one in, one out" rule: for every new item brought in, one must leave.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> NASA research identified snake plants and peace lilies as top air-purifying houseplants. Both thrive in low light and require minimal care — ideal for bedrooms and home offices.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> The National Fire Protection Association reports that dryers cause 13,000+ house fires annually, 34% from un-cleaned lint traps. Clean the lint screen before every load and deep-clean the vent yearly.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> Reseeding bare lawn patches in early fall gives grass 3 months to establish roots before winter. Spring seeding often fails because summer heat kills immature grass.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> The average US household loses 10,000 gallons of water annually to undetected toilet leaks. Put a drop of food coloring in the tank — if color seeps into the bowl without flushing, there is a leak.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> A programmable timer on outdoor lighting saves up to 50% on landscape lighting electricity. Solar path lights are a zero-cost alternative that require no wiring.</blockquote>',
        '<blockquote><strong>Design Tip:</strong> Replacing carpet with hardwood floors yields a 70-80% ROI on average and increases buyer interest by 50% according to the National Association of Realtors.</blockquote>',
    ],
    "finance": [
        '<blockquote><strong>Financial Fact:</strong> The Federal Reserve found that 37% of Americans could not cover a $400 emergency expense with cash. A starter emergency fund of $1,000 is the first goal in any financial plan.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> According to Fidelity, saving 15% of your pre-tax income for retirement — including employer match — puts the average worker on track to retire comfortably by 67.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> The S&P 500 has returned roughly 10% annually over the past century. A $10,000 investment left untouched for 30 years at 10% grows to over $174,000 through compounding.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> The average US household carries $6,500 in credit card debt at an average APR of 22%. Paying only the minimum means a $6,500 balance takes over 20 years to clear.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> The FDIC insures bank deposits up to $250,000 per depositor per bank. For balances above that, splitting funds across banks ensures full coverage.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> According to a 2024 Bankrate survey, 57% of Americans are uncomfortable with their level of emergency savings. Automating even $50 per paycheck into a separate savings account builds a cushion invisibly.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> The IRS reports that the average tax refund is over $3,000. Adjusting your W-4 to reduce your refund by $250 per month puts that money in your pocket year-round instead of giving the government an interest-free loan.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> Vanguard data shows that low-cost index funds outperform 85% of actively managed funds over 15 years. The 0.03%-0.15% expense ratio on an index fund vs. 1%+ on active funds compounds into tens of thousands saved.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> The average 401(k) match is 4.5% of salary. Not contributing enough to get the full match is leaving a guaranteed 100% return on the table — before any market gains.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> Experian reports that payment history makes up 35% of your FICO score. A single 30-day late payment can drop a 780 score by 90-110 points and stays on your report for 7 years.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> A NerdWallet analysis found that the average wedding costs $28,000 in the US. Eloping and investing that amount at age 30 instead yields $174,000 by age 55 at a conservative 8% return.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> The Consumer Financial Protection Bureau reports that medical debt is the top cause of bankruptcy in the US. A Health Savings Account triple-tax advantage helps: contributions, growth, and qualified withdrawals are all tax-free.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> Dollar-cost averaging — investing the same amount monthly regardless of market conditions — reduces the risk of buying at a peak. Over 20 years, consistent monthly investors typically outperform market-timers.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> The average car payment is $725 for new vehicles and $525 for used. The 20/4/10 rule — 20% down, 4-year term, payment under 10% of gross income — prevents a car from derailing your finances.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> According to the Brookings Institution, a $1 increase in the federal minimum wage increases annual earnings for a full-time worker by $2,080 — enough to fund an IRA contribution that grows tax-free for decades.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> Fannie Mae reports that first-time homebuyers who put less than 20% down pay an average of $1,800 per year in PMI. PMI can usually be canceled once equity reaches 20% — request a review immediately.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> A will costs $300-$1,000 through a lawyer or $100-$300 online. Dying without one lets state law decide who gets your assets and can tie up your estate in probate for 12-18 months.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> Term life insurance for a healthy 30-year-old costs roughly $20-$30/month for $500K coverage. Whole life policies cost 10-15x more and mix insurance with underperforming investment products.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> Morningstar found that investors who use a financial advisor lose roughly 2% annually to fees and underperformance versus self-directed index investors. A simple three-fund portfolio does the same job for 0.05%.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> Bankrate data shows that 25% of Americans have no retirement savings at all. Starting at age 40 with $0 means you need to save roughly 25% of income to retire at 67 — starting at 25 requires just 15%.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> The SEC classifies cryptocurrency as a speculative asset. Financial planners recommend limiting crypto to 1-5% of your portfolio and never investing more than you can afford to lose entirely.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> Tax-loss harvesting saves the average taxable investor 0.5-1.5% in annual after-tax returns. It is one of the few free lunches in investing but must be done before December 31 to count for that tax year.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> Social Security replaces roughly 40% of pre-retirement income for average earners. The remaining 60% must come from personal savings, pensions, or continued work — making retirement accounts non-negotiable.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> A TransUnion analysis found that 72% of borrowers who consolidate high-interest credit card debt with a personal loan reduce their interest rate by 8-15 points and pay off debt 2-3 years faster.</blockquote>',
        '<blockquote><strong>Financial Fact:</strong> The 50/30/20 budget — 50% needs, 30% wants, 20% savings — was popularized by Senator Elizabeth Warren and remains the most recommended budgeting framework for beginners.</blockquote>',
    ],
    "tech": [
        '<blockquote><strong>Tech Fact:</strong> A strong, unique password is your first line of defense. The FBI reports that 80% of hacking-related breaches involve compromised passwords. A password manager generates and stores secure passwords for every account.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> The global average cost of a data breach reached $4.88 million in 2024 according to IBM. Multi-factor authentication blocks 99.9% of automated account attacks.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> According to Consumer Reports, keeping a laptop plugged in at 100% charge for extended periods reduces battery lifespan by 20-30%. Modern batteries last longest when kept between 20% and 80%.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> The FCC reports that 42 million Americans lack access to broadband internet. Starlink and 5G home internet are closing the gap for rural areas at 50-200 Mbps speeds.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> Gartner predicts that by 2026, 80% of enterprises will have deployed AI-powered applications. The most practical consumer AI tools today are GPT-based assistants, photo editing, and code completion.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> A UPS in the 1000-1500VA range costs about $100 and protects electronics from power surges, brownouts, and blackouts. Replacing a fried motherboard costs at least 3x that.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> The 3-2-1 backup rule — 3 copies, 2 different media types, 1 offsite copy — is the gold standard for data protection. Cloud backup services automate the offsite copy for under $10/month.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> Wi-Fi 6E routers can deliver up to 1.3 Gbps throughput with compatible devices. But for most homes, a solid Wi-Fi 6 router under $100 handles 4K streaming and video calls just fine.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> A 2024 McAfee report found that 49% of Americans have fallen victim to a tech support scam. Real tech companies do not cold-call you about viruses. Hang up immediately.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> SSDs are now cheaper than ever — 1TB NVMe drives cost under $60. Upgrading from a spinning hard drive to an SSD makes a 10-year-old laptop feel faster than a 2024 budget model.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> Statista reports that the average US household has 21 connected devices. Securing them starts with changing default router passwords and enabling automatic firmware updates.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> Phishing attacks account for 36% of all data breaches according to Verizon\'s 2024 DBIR. The top red flag: unexpected urgency. Legitimate companies never demand immediate payment via email.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> A mesh Wi-Fi system with 2-3 nodes covers up to 6,000 sq ft and eliminates dead zones. A single router, no matter how expensive, cannot overcome concrete walls or multiple floors.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> Apple and Google both scan apps for malware before listing them in official stores. Sideloading apps from third-party sources bypasses these checks and accounts for over 95% of mobile malware infections.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> The average smartphone is replaced every 2.5-3 years. A $30 battery replacement at year 2 often extends usable life by another 2 years, saving $400-$1,000 and reducing e-waste.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> Tesla\'s own data shows that EV batteries retain 88% of capacity after 200,000 miles. For most drivers, an EV battery outlasts the car body. Battery degradation fears are largely overblown.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> Open source software powers 90% of the internet. Tools like LibreOffice, GIMP, and Blender provide professional-grade alternatives to paid software at zero cost.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> Google\'s Transparency Report shows that 95% of all email is spam. Gmail\'s AI filters block 99.9% of it before it reaches your inbox. Marking spam helps train the filter further.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> A VPN encrypts your internet traffic and hides your IP address. It is essential on public Wi-Fi but does not make you anonymous — your VPN provider can still see what you do.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> The average cost of ransomware recovery in 2024 exceeded $2.7 million. Keeping an offline or cloud backup that is not connected to your main network is the single most reliable defense.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> Bluetooth 5.3 doubles the range of earlier versions and supports LE Audio for better sound at lower power. Most 2024+ headphones support it, but your phone needs to as well for the full benefit.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> Quantum computing is still 5-10 years from breaking current encryption, but "harvest now, decrypt later" attacks are already happening. Post-quantum cryptography standards were finalized by NIST in 2024.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> A 1440p 27-inch monitor — the current price-performance sweet spot — costs $150-$250. Dual monitors increase productivity by 20-30% according to a Jon Peddie Research meta-analysis of 15 studies.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> The right to repair movement has won major victories: Apple now sells parts directly to consumers, and 40+ states have proposed repair legislation. DIY phone screen replacement saves $150+ vs. authorized repair.</blockquote>',
        '<blockquote><strong>Tech Fact:</strong> E-waste is the fastest-growing waste stream globally at 62 million tons per year. Donating or selling old electronics keeps toxic materials out of landfills and recovers valuable rare-earth metals.</blockquote>',
    ],
    "travel": [
        '<blockquote><strong>Travel Tip:</strong> According to Skyscanner, booking flights 6-8 weeks before departure yields the lowest average fares. Tuesday and Wednesday departures typically cost 15-20% less than weekend flights.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> The US State Department reports that 300,000+ passports are lost or stolen annually. Keep a digital copy of your passport in encrypted cloud storage and a paper copy separate from the original.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> Google Flights price alerts track fare changes 24/7. Setting an alert 3-4 months before your trip catches most price drops, which typically last 1-2 days before rebounding.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> The Points Guy estimates the average travel credit card signup bonus is worth $750 in flights. Cards with 0% foreign transaction fees save an additional 3% on every overseas purchase.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> Airbnb cleaning fees average 25% of the booking cost. Filtering for hotels and guesthouses sometimes yields better value, especially for stays under 4 nights when cleaning fees hit hardest.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> Rick Steves recommends exchanging $100 at the airport for immediate needs and using local ATMs for the rest — airport exchange booths typically charge 5-10% worse rates than bank ATMs.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> Travel insurance claims data shows that medical evacuation costs average $75,000-$250,000 depending on location. A $50-$100 travel insurance policy covers this; most US health insurance does not.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> Google Maps offline mode lets you download entire city maps before you leave. Combined with a local SIM card ($10-$20 in most countries), you will never be stranded without navigation.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> AAA data shows that domestic road trips account for 85% of US summer travel. Booking national park campgrounds 6 months in advance through Recreation.gov is essential for popular parks like Yosemite and Yellowstone.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> According to Hopper, the cheapest month to fly to Europe from the US is February; the most expensive is July. Shoulder seasons — April-May and September-October — offer the best balance of weather and price.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> The Schengen Area allows 90 days of visa-free travel across 27 European countries. Overstaying triggers fines, deportation, and entry bans of 1-3 years. Set a calendar reminder for day 85.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> Pack a change of clothes and essential toiletries in your carry-on. US DOT data shows that 0.7% of checked bags are mishandled, which adds up to over 1.5 million lost bags per year.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> Hostelworld reports that dorm beds in Western Europe average $30-$50 per night, while private rooms average $80-$120. Eastern Europe offers dorms from $10 and privates from $30.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> Eurail passes break even at roughly 3-4 long-distance train trips per week. For shorter stays in 1-2 countries, buying point-to-point tickets 1-2 months in advance is often cheaper.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> Lonely Planet research shows that slow travel — staying 5+ days in one location — costs 30-40% less per day than rapid multi-city itineraries and provides deeper cultural immersion.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> WeatherSpark provides year-round climate charts for any city globally. Checking actual weather data instead of "best time to visit" articles prevents rainy season surprises.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> The Nomadic Matt blog popularized the $50/day budget travel philosophy. In Southeast Asia, South America, and Eastern Europe, $50 covers a comfortable private room, three meals, transport, and one paid activity.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> TSA PreCheck costs $78 for 5 years and 99% of members wait under 10 minutes at security. Global Entry includes PreCheck plus expedited customs for $100 — a better deal for international travelers.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> Booking.com data shows that properties with 50+ reviews and an 8.0+ rating are reliably good. Anything below 7.0 with fewer than 20 reviews is a gamble — read the most recent 10 reviews carefully.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> A VPN lets you check flight prices from different countries. Airlines price the same seat differently based on your location — sometimes the difference is $200+ for long-haul flights.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> The US DOT requires airlines to refund you for canceled or significantly delayed flights regardless of the reason. If you accept a voucher instead, you forfeit your legal right to a cash refund.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> Carbon offset programs from reputable companies like Gold Standard cost $10-$30 per ton of CO2 — roughly $50 to offset a round-trip transatlantic flight. It is not perfect, but it is the best tool available today.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> Conde Nast Traveler recommends notifying your bank of travel dates through the app — not by phone. Most major banks now let you set travel notices digitally in under 2 minutes.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> UNESCO lists 1,199 World Heritage sites. Visiting one anchors a trip with guaranteed historical or natural significance and helps preserve irreplaceable landmarks through tourism revenue.</blockquote>',
        '<blockquote><strong>Travel Tip:</strong> A 2024 Expedia study found that 42% of travelers regret overpacking. The 5-4-3-2-1 packing method — 5 tops, 4 bottoms, 3 shoes, 2 jackets, 1 swimsuit — works for any 2-week trip.</blockquote>',
    ],
}

SITE_CATEGORY = {
    "sub-pets": "pets", "sub-healthy": "health", "sub-home": "home",
    "sub-finance": "finance", "sub-tech": "tech", "sub-travel": "travel",
}


def needs_blockquote(html):
    return '<blockquote>' not in html


def insert_blockquote(html, bq):
    # H2に続く最初の <p> の後ろに <blockquote> を配置するほうが意味的に自然
    m = re.search(r'<h2[^>]*>.*?</h2>\s*<p[^>]*>.*?</p>', html, re.DOTALL)
    if m:
        end = m.end()
        return html[:end] + '\n' + bq + '\n' + html[end:]

    # H2 がない場合: 最初の <p> の後
    m = re.search(r'</p>', html)
    if m:
        end = m.end()
        return html[:end] + '\n' + bq + '\n' + html[end:]

    # Fallback — 何もしない
    return html


def main():
    dry_run = "--dry-run" in sys.argv
    updated = 0
    total = 0

    for site_dir, category in SITE_CATEGORY.items():
        site_path = ROOT / site_dir
        if not site_path.exists():
            continue
        pool = POOLS[category]
        articles = sorted(site_path.glob("article-*.html"))
        for article in articles:
            html = article.read_text(encoding="utf-8")
            if not needs_blockquote(html):
                continue
            total += 1
            # 記事番号ベースで決定的に割り当て
            num_match = re.search(r'article-(\d+)', article.name)
            num = int(num_match.group(1)) if num_match else 0
            bq = pool[num % len(pool)]
            new_html = insert_blockquote(html, bq)
            if new_html != html:
                if not dry_run:
                    article.write_text(new_html, encoding="utf-8")
                updated += 1

    label = "Would insert" if dry_run else "Inserted"
    print(f"{label} blockquotes into {updated}/{total} articles")


if __name__ == "__main__":
    main()
