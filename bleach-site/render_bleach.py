#!/usr/bin/env python3
"""Render all Bleach Wiki HTML files."""

import os

BASE_DIR = "d:/AI网站文件夹/bleach-site"
IMG_DIR = os.path.join(BASE_DIR, "images")

SITE_NAME = "Bleach Wiki"
SITE_DESC = "Your ultimate guide to the Bleach universe — character profiles, Zanpakuto guides, story arcs, Soul Society lore, and more."
DOMAIN = "bleach.jycsd.com"
ADSENSE = "ca-pub-2595917642864488"
GA4 = "G-GGNWR1X1GV"
ACCENT = "#f39c12"
ACCENT_LIGHT = "#f1c40f"
BG_DARK = "#0d1117"
BG_CARD = "#161b22"
BG_NAV = "#0d1117"

ONERROR_SVG = "this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22400%22><rect fill=%22%23161b22%22 width=%22400%22 height=%22400%22/><text fill=%22%23f39c12%22 font-size=%2220%22 x=%2250%%22 y=%2250%%22 text-anchor=%22middle%22 dominant-baseline=%22middle%22>Bleach</text></svg>'"

# ============================================================
# CHARACTER DATA
# ============================================================
CHARACTERS = [
    {
        "slug": "ichigo-kurosaki",
        "name": "Ichigo Kurosaki",
        "title": "Substitute Soul Reaper",
        "affiliation": "Substitute Soul Reaper, Kurosaki Family",
        "rank": "Substitute Soul Reaper",
        "overview": "Ichigo Kurosaki is the main protagonist of the Bleach series. He is a teenager who unexpectedly gains the powers of a Soul Reaper after meeting Rukia Kuchiki. Throughout the series, Ichigo grows from a reluctant hero into a powerful warrior, protecting his friends and family from various supernatural threats.",
        "appearance": "Ichigo is a tall teenager with distinctive orange hair and brown eyes. He typically wears the standard black Shinigami shihakusho when in his Soul Reaper form, carrying a massive zanpakuto named Zangetsu on his back. In his human form, he wears the standard school uniform of Karakura High School.",
        "personality": "Ichigo is fiercely protective of his friends and family, often rushing into danger without hesitation. He has a strong sense of justice and refuses to back down from any challenge. Despite his hot-headed exterior, he is deeply caring and carries the weight of protecting others on his shoulders.",
        "abilities": "As a Substitute Soul Reaper, Ichigo possesses immense spiritual pressure and combat skills. His zanpakuto Zangetsu is a constant-release type, and he masters techniques including Getsuga Tensho and Bankai: Tensa Zangetsu. He also develops Hollow and Quincy powers inherited from his lineage.",
        "trivia": "Ichigo's name means 'strawberry' and 'protector' in Japanese. His voice actors are Masakazu Morita (Japanese) and Johnny Yong Bosch (English). He is ranked as one of the most popular anime protagonists of all time in multiple fan polls."
    },
    {
        "slug": "rukia-kuchiki",
        "name": "Rukia Kuchiki",
        "title": "Lieutenant of 13th Division",
        "affiliation": "Gotei 13, 13th Division",
        "rank": "Lieutenant",
        "overview": "Rukia Kuchiki is a Soul Reaper assigned to the 13th Division of the Gotei 13. She is the adopted sister of Byakuya Kuchiki and plays a pivotal role in the series as the one who gives Ichigo his Soul Reaper powers. Her journey from a guilt-ridden past to finding true friendship is central to her character.",
        "appearance": "Rukia has short black hair with distinctive sidelocks and violet eyes. She is petite in stature but carries herself with dignity. She wears the standard Soul Reaper uniform and later dons a white cape as a lieutenant. Her zanpakuto, Sode no Shirayuki, is elegant and slender.",
        "personality": "Rukia is serious, disciplined, and deeply loyal to her duties as a Soul Reaper. She has a sharp wit and is not afraid to speak her mind. Beneath her stoic exterior, she cares deeply for her friends and carries profound love for her late sister Hisana.",
        "abilities": "Rukia is a skilled kido practitioner with expertise in demon arts. Her zanpakuto Sode no Shirayuki is an ice-type with abilities including 'Some no Mai: Tsukishiro' and 'Hakuren.' Her Bankai, Hakka no Togame, temporarily freezes her body to achieve absolute zero.",
        "trivia": "Rukia's name comes from the Japanese word for 'light.' She was originally intended to be the main protagonist before the focus shifted to Ichigo. Her relationship with Renji is one of the most beloved dynamics in the series."
    },
    {
        "slug": "renji-abarai",
        "name": "Renji Abarai",
        "title": "Lieutenant of 6th Division",
        "affiliation": "Gotei 13, 6th Division",
        "rank": "Lieutenant",
        "overview": "Renji Abarai is the Lieutenant of the 6th Division under Captain Byakuya Kuchiki. He grew up in the Rukongai with Rukia and considers her his closest friend. His journey from a street orphan to a powerful Soul Reaper officer is marked by determination and fierce loyalty.",
        "appearance": "Renji is tall with bright red hair styled in a spiky ponytail. His body is covered in intricate tattoos, and he has a piercing gaze. He wears the standard lieutenant's uniform with a white haori and carries his unique zanpakuto, Zabimaru, which has a distinctive segmented blade.",
        "personality": "Renji is boisterous, competitive, and passionate. He wears his heart on his sleeve and is quick to anger but equally quick to laugh. Despite his rough exterior, he is deeply honorable and values his friendships above all else.",
        "abilities": "Renji wields Zabimaru, a baboon-and-snake-type zanpakuto that can extend its segmented blade. His Shikai releases Hihio Zabimaru, and his Bankai, Soo Zabimaru, creates a massive skeletal snake form. He is also proficient in hand-to-hand combat.",
        "trivia": "Renji's tattoos are a symbol of his Rukongai origins. The name 'Renji' can mean 'love letter' in Japanese. His dynamic with Rukia is one of the longest-running relationships in the series, spanning from childhood to adulthood."
    },
    {
        "slug": "byakuya-kuchiki",
        "name": "Byakuya Kuchiki",
        "title": "Captain of 6th Division",
        "affiliation": "Gotei 13, 6th Division",
        "rank": "Captain",
        "overview": "Byakuya Kuchiki is the 28th head of the Kuchiki Clan and Captain of the 6th Division. He is Rukia's adoptive brother and one of the most powerful Soul Reapers in the Gotei 13. His character arc explores the conflict between duty and personal attachment.",
        "appearance": "Byakuya has long black hair, pale skin, and distinctive white eyes. He wears the standard captain's haori with a white scarf-like sash called a ginpaku kazaguruma. He carries Senbonzakura, which is said to be one of the most beautiful zanpakuto in Soul Society.",
        "personality": "Byakuya is calm, stoic, and strictly adheres to the laws and traditions of Soul Society. He speaks with a quiet authority and rarely shows emotion. However, beneath his cold exterior lies a deep capacity for love and loyalty, particularly toward his late wife Hisana and sister Rukia.",
        "abilities": "Byakuya wields Senbonzakura, a zanpakuto that scatters into thousands of razor-sharp cherry blossom petals. His Bankai, Senbonzakura Kageyoshi, creates massive blade pillars. He is a master of flash step (shunpo) and precision combat.",
        "trivia": "Byakuya's name means 'white night.' His character design was inspired by traditional Japanese nobility. The scattering of Senbonzakura's petals is considered one of the most visually iconic techniques in anime."
    },
    {
        "slug": "toshiro-hitsugaya",
        "name": "Toshiro Hitsugaya",
        "title": "Captain of 10th Division",
        "affiliation": "Gotei 13, 10th Division",
        "rank": "Captain",
        "overview": "Toshiro Hitsugaya is the youngest captain in the history of the Gotei 13, leading the 10th Division as a prodigy. He is childhood friends with Momo Hinamori and carries the burden of incredible power at a young age. His ice-type zanpakuto is among the strongest in Soul Society.",
        "appearance": "Toshiro has short white hair and turquoise eyes, giving him a distinctive youthful appearance. He wears the standard captain's haori and carries Hyorinmaru, a katana with a square tsuba. Despite his young looks, he carries himself with the dignity of a captain.",
        "personality": "Toshiro is mature beyond his years, serious, and dedicated to his duties. He can be short-tempered when underestimated due to his age but is incredibly intelligent and strategic. He is fiercely protective of those close to him, especially Momo.",
        "abilities": "Toshiro's zanpakuto Hyorinmaru is the strongest ice-type in Soul Society. His Shikai commands ice and water, while his Bankai, Daiguren Hyorinmaru, creates an ice dragon with devastating freezing abilities. He can achieve a mature Bankai form at full power.",
        "trivia": "Toshiro's birthday is December 20th. His white hair is natural and linked to his zanpakuto's ice powers. He is consistently one of the most popular characters in Bleach character popularity polls."
    },
    {
        "slug": "kenpachi-zaraki",
        "name": "Kenpachi Zaraki",
        "title": "Captain of 11th Division",
        "affiliation": "Gotei 13, 11th Division",
        "rank": "Captain",
        "overview": "Kenpachi Zaraki is the fierce and battle-hungry Captain of the 11th Division. He achieved his position by defeating the previous captain in single combat and runs his division with a simple philosophy: strength is everything. His love for battle is matched only by his growing bond with his lieutenant Yachiru.",
        "appearance": "Kenpachi is a massive man with wild black hair and a permanent grin. His face bears a prominent scar over his left eye and another on his forehead from childhood battles. He wears a tattered captain's haori over his standard uniform and carries his zanpakuto casually.",
        "personality": "Kenpachi lives for the thrill of combat, seeking powerful opponents to test his strength. He is brutally honest, straightforward, and has no interest in politics or strategy. Despite his savage nature, he has a code of honor and respects those who can fight him seriously.",
        "abilities": "Kenpachi fights with raw physical power rather than techniques. He has immense spiritual pressure and durability. After connecting with his zanpakuto, he learns its name is Nozarashi and achieves Bankai, becoming one of the most powerful captains.",
        "trivia": "Kenpachi is a title given to the strongest Soul Reaper of an era, not a personal name. His patch over the right eye absorbs his power so he can enjoy fights longer. Despite his intimidating appearance, he has a soft spot for his lieutenant Yachiru."
    },
    {
        "slug": "sosuke-aizen",
        "name": "Sosuke Aizen",
        "title": "Former Captain of 5th Division",
        "affiliation": "Former Gotei 13, Arrancar Army, Royal Palace",
        "rank": "Former Captain",
        "overview": "Sosuke Aizen is the primary antagonist of the Bleach series. Formerly the kind and gentle Captain of the 5th Division, he orchestrated an elaborate century-long conspiracy to overthrow the Soul King and reshape reality. His manipulation and schemes span the entire first half of the series.",
        "appearance": "Aizen has brown hair, brown eyes, and a calm, handsome appearance. He wears glasses and carries himself with an air of sophistication. After revealing his true nature, his appearance shifts to reflect his arrogance — with slicked-back hair and a confident smirk.",
        "personality": "Aizen is brilliant, manipulative, and supremely confident in his own superiority. He views himself as a transcendent being destined to rule. He is patient and calculating, able to maintain a false persona for over a century to execute his plans.",
        "abilities": "Aizen's zanpakuto Kyoka Suigetsu has complete hypnosis — the most dangerous illusion ability in the series. He is a master of kido, swordsmanship, and has immense spiritual pressure. After fusing with the Hogyoku, he achieves a transcendent form beyond Soul Reaper and Hollow.",
        "trivia": "Aizen's theme music is classical symphony, reflecting his refined nature. His famous line 'Since when were you under the impression that I wasn't using Kyoka Suigetsu?' is one of anime's most iconic twists. He defeated multiple captains simultaneously without his zanpakuto."
    },
    {
        "slug": "orihime-inoue",
        "name": "Orihime Inoue",
        "title": "High School Student",
        "affiliation": "Karakura Town",
        "rank": "Civilian",
        "overview": "Orihime Inoue is one of Ichigo's closest friends and a kind-hearted girl with extraordinary powers. She develops the ability to reject phenomena through her hairpins, which manifest as fairies. Her emotional strength and unwavering faith in her friends make her an irreplaceable member of the group.",
        "appearance": "Orihime has long, vibrant orange hair that she typically wears with distinctive hairpins shaped like six-petaled flowers. She has large brown eyes and a warm smile. She usually wears the Karakura High School uniform or casual feminine clothing.",
        "personality": "Orihime is gentle, optimistic, and deeply caring toward everyone around her. She often speaks her mind with childlike honesty and has a strong moral compass. Despite her kindness, she possesses incredible emotional fortitude and stands firm in her beliefs.",
        "abilities": "Orihime's power, Shun Shun Rikka, is manifested through six fairies from her hairpins. Her abilities reject phenomena: Santen Kesshun creates a defensive barrier, Koten Zanshun attacks, and Soten Kisshun heals by rejecting damage. Her power borders on reality manipulation.",
        "trivia": "Orihime's hairpins become fairies named Tsubaki, Ayame, Shun'o, Hinagiku, Lily, and Baigon. She has a peculiar obsession with all things cute and often imagines talking animals. Her cooking is famously terrible, creating bizarre dishes that defy explanation."
    },
    {
        "slug": "uryu-ishida",
        "name": "Uryu Ishida",
        "title": "Quincy",
        "affiliation": "Quincy, Karakura Town",
        "rank": "Last Quincy",
        "overview": "Uryu Ishida is the last surviving Quincy of the Ishida bloodline and a classmate of Ichigo. Initially antagonistic toward Soul Reapers due to historical Quincy persecution, he evolves into a trusted ally and friend. His pride and skill as a Quincy make him a formidable fighter.",
        "appearance": "Uryu has short black hair and wears glasses, giving him a studious appearance. He typically wears the Karakura High School uniform but don his Quincy uniform — a white hakama-like outfit — in battle. He carries his Quincy bow, which manifests from reishi.",
        "personality": "Uryu is proud, intelligent, and initially rigid in his beliefs. He maintains a cool and aloof demeanor but has a strong sense of justice and fairness. His rivalry with Ichigo pushes him to grow, and he eventually acknowledges Soul Reapers as worthy allies.",
        "abilities": "Uryu is a master of Quincy techniques including Heilig Pfeil (sacred arrows) and Hirenkyaku (high-speed movement). He uses various Ginto (spirit tools) and has advanced techniques like Sprenger and Licht Regen. He develops the Vollstandig power later in the series.",
        "trivia": "Uryu's grandfather Souken Ishida was killed by Mayuri Kurotsuchi, creating a deep hatred. His father Ryuken Ishida is a doctor and also a Quincy of immense power. Uryu's sense of fashion is particularly traditional for his age."
    },
    {
        "slug": "yasutora-sado",
        "name": "Yasutora Sado",
        "title": "High School Student",
        "affiliation": "Karakura Town",
        "rank": "Civilian",
        "overview": "Yasutora 'Chad' Sado is Ichigo's loyal best friend, a gentle giant of Mexican-Japanese heritage. Despite his intimidating size and strength, Chad is peaceful and soft-spoken. He develops Fullbring powers that manifest through his arms, becoming a protector of those who cannot protect themselves.",
        "appearance": "Chad is exceptionally tall and muscular with dark skin. He has short black hair and often wears gold chain necklaces and loose-fitting clothing. In battle, his right arm transforms into a metallic shield-like form (Brazo Derecho de la Garra) and his left into a weapon (Brazo Izquierda del Diablo).",
        "personality": "Chad is quiet, gentle, and speaks only when necessary. He lives by his grandfather's code: 'Never fight unless you have to, but if you must fight, never lose.' He is fiercely loyal to Ichigo and acts as a protective older brother figure to their group.",
        "abilities": "Chad's Fullbring powers manifest through his arms. His right arm becomes the Brazo Derecho de la Garra (Right Arm of the Claw), a massive shield. His left arm becomes Brazo Izquierda del Diablo (Left Arm of the Devil), a devastating weapon. He later awakens latent Soul Reaper powers.",
        "trivia": "Chad is of Mexican-Japanese descent. After the series, he becomes a professional boxer. Despite his frequent fights, he fundamentally dislikes violence and sees it as a last resort."
    },
    {
        "slug": "mayuri-kurotsuchi",
        "name": "Mayuri Kurotsuchi",
        "title": "Captain of 12th Division",
        "affiliation": "Gotei 13, 12th Division, Shinji Research & Development",
        "rank": "Captain",
        "overview": "Mayuri Kurotsuchi is the eccentric and ruthless Captain of the 12th Division and president of the Shinji Research and Development Institute. A mad scientist at heart, he views everything and everyone as subjects for his experiments. His genius-level intellect is matched only by his complete lack of ethics.",
        "appearance": "Mayuri has painted white skin and black markings around his eyes, giving him a terrifying clown-like appearance. He wears a modified captain's haori with a striped scarf and carries a zanpakuto shaped like a curved nail. His appearance changes between arcs as he modifies his body.",
        "personality": "Mayuri is cold, calculating, and utterly amoral. He sees the value of life only in terms of scientific interest and is willing to sacrifice anyone for research. He has a grandiose sense of his own genius and becomes enraged when someone interferes with his experiments.",
        "abilities": "Mayuri's zanpakuto Ashisogi Jizo paralyzes opponents and can transform into a giant larvae-like form. His Bankai, Konjiki Ashisogi Jizo, creates a massive caterpillar monster that releases deadly poison. He has extensively modified his own body with various enhancements and backups.",
        "trivia": "Mayuri has survived death multiple times by modifying his body. He was imprisoned in the Maggot's Nest for his unethical experiments before being recruited. His lieutenant Nemu was created by him as an artificial Soul Reaper."
    },
    {
        "slug": "shunsui-kyoraku",
        "name": "Shunsui Kyoraku",
        "title": "Captain of 8th Division / Head Captain",
        "affiliation": "Gotei 13, 8th Division",
        "rank": "Captain / Head Captain",
        "overview": "Shunsui Kyoraku is the easygoing Captain of the 8th Division who later becomes Head Captain of the Gotei 13. He is one of the oldest and most experienced Soul Reapers, having been a captain for over a thousand years. His laid-back demeanor hides deadly skill and deep wisdom.",
        "appearance": "Shunsui has long brown hair tied in a ponytail, wears a traditional straw hat (kasa), and a pink flowered haori over his captain's uniform. He is rarely seen without the hat or his dual zanpakuto. His appearance gives him a casual, almost lazy impression.",
        "personality": "Shunsui appears perpetually relaxed, lazy, and fond of drinking sake. He speaks in a playful manner and avoids serious conversations when possible. However, beneath this facade lies a sharp strategist, a fierce warrior, and someone who deeply understands the weight of leadership and sacrifice.",
        "abilities": "Shunsui wields a dual-bladed zanpakuto, Katen Kyokotsu. His Shikai creates childlike games (children's games) that both players must follow. His Bankai, Katen Kyokotsu: Karamatsu Shinju, is a melancholic theatrical performance that forces opponents into tragic roles with lethal consequences.",
        "trivia": "Shunsui was a student of Yamamoto alongside Jushiro Ukitake. His relationship with Nanao Ise involves her family inheritance of a forbidden kido. He becomes Head Captain after Yamamoto's death, taking on the role reluctantly."
    },
    {
        "slug": "jushiro-ukitake",
        "name": "Jushiro Ukitake",
        "title": "Captain of 13th Division",
        "affiliation": "Gotei 13, 13th Division",
        "rank": "Captain",
        "overview": "Jushiro Ukitake is the kind and gentle Captain of the 13th Division, suffering from a chronic illness that has plagued him since childhood. Despite his frail health, he is one of the most powerful and respected Soul Reapers in history. His mentorship of Rukia and his bond with Shunsui Kyoraku define much of his story.",
        "appearance": "Jushiro has long white hair tied back and tired, kind eyes. He is tall but thin, often seen coughing into a handkerchief. He wears the standard captain's haori and carries his unique zanpakuto, which has a split blade connected by a cord.",
        "personality": "Jushiro is warm, compassionate, and deeply empathetic. He treats everyone with kindness and believes in redemption and understanding. Despite his gentle nature, he is fiercely protective of his subordinates and will fight with everything he has when necessary.",
        "abilities": "Jushiro's zanpakuto Sogyo no Kotowari is a dual-blade connected by a cord that can absorb and redirect energy attacks. His abilities include defensive and counter techniques. He is a skilled kido practitioner and master strategist despite his illness.",
        "trivia": "Jushiro's illness is stated to be a lung disease, though its exact nature is never revealed. He was saved as a child by Mimihagi, the right hand of the Soul King. His character is based on the Japanese concept of a noble and tragic warrior."
    },
    {
        "slug": "yoruichi-shihoin",
        "name": "Yoruichi Shihoin",
        "title": "Former Captain / Flash Goddess",
        "affiliation": "Shihoin Clan, Former Gotei 13",
        "rank": "Former Captain",
        "overview": "Yoruichi Shihoin is a former Captain of the 2nd Division and former commander of the Onmitsukido secret corps. She is known as the 'Flash Goddess' for her unparalleled speed and mastery of flash step. For over a century, she operated in exile alongside Kisuke Urahara, aiding Ichigo and his friends.",
        "appearance": "Yoruichi has dark skin, golden eyes, and long black hair that she typically wears in a ponytail. She is athletic and graceful, often wearing form-fitting combat clothing. She can also transform into a slim black cat, a form she used while in exile in the human world.",
        "personality": "Yoruichi is confident, witty, and highly intelligent. She has a playful teasing side, especially with Kisuke and Ichigo, but is ruthlessly serious in battle. She is fiercely loyal to her friends and carries deep responsibility for the events that led to her exile.",
        "abilities": "Yoruichi is unmatched in shunpo (flash step), earning her the title of 'Flash Goddess.' She excels in hand-to-hand combat and Hakuda techniques. Her techniques include Shunko, which combines kido with hand-to-hand combat, creating devastating energy attacks.",
        "trivia": "Yoruichi's cat form was a long-running gag in the series. She hails from the noble Shihoin Clan, one of the four great noble families of Soul Society. Her relationship with Kisuke Urahara is one of deep trust and mutual respect built over centuries."
    },
    {
        "slug": "grimmjow-jaegerjaquez",
        "name": "Grimmjow Jaegerjaquez",
        "title": "Sexta Espada",
        "affiliation": "Arrancar Army",
        "rank": "Sexta Espada (6th)",
        "overview": "Grimmjow Jaegerjaquez is the Sexta (Sixth) Espada in Aizen's Arrancar army. A prideful and battle-hungry warrior, he quickly becomes one of Ichigo's most personal rivals. His desire to prove himself as the king of combat drives him through every confrontation.",
        "appearance": "Grimmjow has turquoise hair, blue markings beneath his eyes, and a piercing gaze. He wears the standard white Arrancar jacket with the Espada rank tattooed on his back. He has a distinctive grin that reveals his feral nature and his hollow mask fragment sits on his jaw.",
        "personality": "Grimmjow is arrogant, aggressive, and obsessed with fighting strong opponents. He values strength above all else and despises weakness in himself and others. Despite being aligned with Aizen, he follows his own code of honor and refuses to kill those he considers weak.",
        "abilities": "Grimmjow's zanpakuto is Pantera, which transforms his hands into massive feline claws. He can release his Resurreccion to become a panther-like beast with devastating speed and power. His techniques include Desgarron and Gran Rey Cero.",
        "trivia": "Grimmjow's number 6 is tattooed on his lower back. 'Jaegerjaquez' German translates roughly to 'hunter of something.' He survives the Thousand-Year Blood War and later resurfaces in the Hell arc as one of the few Arrancar still active."
    },
    {
        "slug": "ulquiorra-cifer",
        "name": "Ulquiorra Cifer",
        "title": "Cuatro Espada",
        "affiliation": "Arrancar Army",
        "rank": "Cuatro Espada (4th)",
        "overview": "Ulquiorra Cifer is the Cuarto (Fourth) Espada and arguably the most enigmatic of Aizen's servants. Emotionless and nihilistic, he views the world through a lens of emptiness. His interactions with Orihime Inoue challenge his core beliefs, making him one of the most complex antagonists in Bleach.",
        "appearance": "Ulquiorra has pale skin, black spiky hair, and distinctive green eyes with slit pupils. He has dark markings under his eyes resembling tear tracks. He wears the white Arrancar uniform and has a unique hollow hole in his chest. His wings have a demonic appearance.",
        "personality": "Ulquiorra is cold, detached, and expresses no emotions. He speaks in monotone and approaches everything with logical analysis. He genuinely believes that the heart is meaningless and that emptiness is the natural state of existence. His growing curiosity about emotions defines his arc.",
        "abilities": "Ulquiorra's zanpakuto Murcielago releases into a bat-like form. He has unique abilities including Cero Oscuras (a black cero) and Lanza del Relampago (a lightning spear of immense destructive power). He can achieve a second Resurreccion stage, Segunda Etapa, unique among Espada.",
        "trivia": "Ulquiorra is the only Espada capable of achieving Segunda Etapa. His name 'Cifer' references Lucifer. His final scene, where he realizes what a 'heart' is moments before dissolving to dust, is considered one of the most tragic and beautiful moments in Bleach."
    },
    {
        "slug": "yamamoto-genryusai",
        "name": "Yamamoto Genryusai",
        "title": "Head Captain of Gotei 13",
        "affiliation": "Gotei 13",
        "rank": "Head Captain / Commander-in-Chief",
        "overview": "Yamamoto Genryusai is the Founder and Head Captain of the Gotei 13, the oldest and most powerful Soul Reaper in existence. With a history spanning over a thousand years, he has shaped Soul Society's military and justice system. His presence alone commands respect and fear from allies and enemies alike.",
        "appearance": "Yamamoto is elderly with a long white beard and numerous scars on his bald head. Despite his age, he has a towering, muscular physique. He wears the traditional head captain's white haori over a black kimono and carries a ornate walking stick which conceals his zanpakuto.",
        "personality": "Yamamoto is stern, no-nonsense, and deeply committed to justice and order. He has little patience for disrespect or chaos and demands absolute discipline from his subordinates. Despite his harsh exterior, he cares deeply for Soul Society and his students, carrying the weight of countless centuries.",
        "abilities": "Yamamoto wields Ryujin Jakka, the oldest and most powerful fire-type zanpakuto. His Shikai engulfs his blade in flames hot enough to destroy anything. His Bankai, Zanka no Tachi, condenses all his fire power into the blade tip, raising his body temperature to 15,000,000 degrees Celsius.",
        "trivia": "Yamamoto founded the Gotei 13 over 1,000 years ago. The flames of Ryujin Jakka are said to be as hot as the sun. His Bankai is considered the strongest fire-type ability in the entire Bleach universe."
    },
    {
        "slug": "gin-ichimaru",
        "name": "Gin Ichimaru",
        "title": "Former Captain of 3rd Division",
        "affiliation": "Former Gotei 13, Aizen's Faction",
        "rank": "Former Captain",
        "overview": "Gin Ichimaru is the enigmatic former Captain of the 3rd Division with a perpetual smile and snake-like demeanor. He serves as Aizen's lieutenant for over a century, keeping his true motives hidden. His character is one of the most layered and surprising in the series.",
        "appearance": "Gin is tall with silver-white hair and narrow, snake-like eyes that he usually keeps closed in a smile. He wears the standard captain's haori and carries a unique zanpakuto that appears to be a simple wakizashi. His appearance is deliberately unsettling and mysterious.",
        "personality": "Gin maintains a constant, chilling smile that never reaches his eyes. He speaks in a soft, polite tone and seems utterly indifferent to the suffering around him. Beneath this facade lies a complex individual whose actions are driven by a deeply personal motivation.",
        "abilities": "Gin's zanpakuto Shinso can extend at incredible speeds, piercing anything in its path. His Bankai, Kamishini no Yari, extends at Mach 500 and has a deadly ability called Buto: this ability doesn't cut but leaves a deadly poison inside the wound. It can retract at the same speed.",
        "trivia": "Gin's true loyalty was always to Rangiku Matsumoto, his childhood friend. His betrayal of Aizen is one of the biggest twists in Bleach. His name 'Gin' means 'silver' in Japanese, reflecting his silver hair and ambiguous nature."
    },
    {
        "slug": "kisuke-urahara",
        "name": "Kisuke Urahara",
        "title": "Former Captain of 12th Division",
        "affiliation": "Former Gotei 13, Urahara Shop",
        "rank": "Former Captain",
        "overview": "Kisuke Urahara is the eccentric former Captain of the 12th Division and founder of the Shinji Research and Development Institute. Exiled from Soul Society over a century ago, he now runs a small shop in Karakura Town while secretly aiding Ichigo and his friends. His genius-level intellect is matched only by his eccentricity.",
        "appearance": "Kisuke has short blond hair and usually wears a green-striped bucket hat and wooden sandals (geta). He typically wears a brown traditional coat called a haori over a dark kimono. He always carries a fan and has an easygoing smile.",
        "personality": "Kisuke is perpetually cheerful and speaks with a deceptively casual tone. He loves teasing others and rarely shows his serious side openly. Behind the facade, he is a brilliant strategist and inventor who carries immense guilt and responsibility for past events.",
        "abilities": "Kisuke's zanpakuto Benihime releases into a cane-like weapon. His abilities include blood mist shields and energy blasts. His Bankai, Kannonbiraki Benihime Aratame, can restructure anything within its range. He is a master of kido, inventions, and strategic planning.",
        "trivia": "Kisuke was responsible for developing the Hogyoku, which sparked the chain of events in the series. He trained Ichigo extensively before the Soul Society arc. His shop in Karakura Town serves as a secret base for the main characters."
    },
    {
        "slug": "isshin-kurosaki",
        "name": "Isshin Kurosaki",
        "title": "Former Captain of 10th Division",
        "affiliation": "Former Gotei 13, Kurosaki Clinic",
        "rank": "Former Captain",
        "overview": "Isshin Kurosaki is Ichigo's eccentric father who runs a small medical clinic in Karakura Town. While he appears to be a goofy single father, Isshin is actually a former Captain of the 10th Division of the Gotei 13. His past as a powerful Soul Reaper and his relationship with Ichigo's mother Masaki shape much of the series' backstory.",
        "appearance": "Isshin is tall and muscular with short black hair and a strong jawline. He typically wears a white doctor's coat over casual clothing. As a Soul Reaper, he wore the captain's haori and carried Engetsu, a katana with a square guard.",
        "personality": "Isshin appears loud, goofy, and overly dramatic in daily life, often performing ridiculous comedic routines. He is a caring and devoted father who deeply loves his children. In battle, he transforms into a serious, focused warrior worthy of his former captain rank.",
        "abilities": "Isshin wields Engetsu, a fire-type zanpakuto with techniques similar to Getsuga Tensho. His combat skills include expert swordsmanship and flash step. He also possesses deep knowledge of Quincy-Hollow interactions from his relationship with Masaki.",
        "trivia": "Isshin's real name is Isshin Shiba of the Shiba Clan. His wife Masaki Kurosaki was a pure-blood Quincy. He gave up his Soul Reaper powers to save Masaki from a Hollow attack, which is why Ichigo inherited such immense potential."
    }
]

# ============================================================
# ZANPAKUTO DATA
# ============================================================
ZANPAKUTO = [
    {"name": "Zangetsu", "owner": "Ichigo Kurosaki", "type": "Constant Release", "desc": "Zangetsu is Ichigo's zanpakuto, a massive blade with no guard that represents his Shinigami powers. In its true form, it manifests as two blades — one black and one white. Getsuga Tensho fires a concentrated energy blast.", "ability": "Getsuga Tensho, Bankai: Tensa Zangetsu"},
    {"name": "Senbonzakura", "owner": "Byakuya Kuchiki", "type": "Scattering", "desc": "Senbonzakura scatters into thousands of razor-sharp cherry blossom petals that can cut anything. Its Bankai, Senbonzakura Kageyoshi, summons massive blade pillars from the ground. One of the most beautiful and deadly zanpakuto.", "ability": "Senbonzakura Kageyoshi, Gokei, Shukei: Hakuteiken"},
    {"name": "Hyorinmaru", "owner": "Toshiro Hitsugaya", "type": "Ice", "desc": "Hyorinmaru is the strongest ice-type zanpakuto, commanding water and ice. Its Bankai, Daiguren Hyorinmaru, creates an ice dragon form. At full power, Hitsugaya achieves a matured Bankai with absolute freezing abilities.", "ability": "Tenshi no Kabe, Guncho Tsurara, Bankai: Daiguren Hyorinmaru"},
    {"name": "Zabimaru", "owner": "Renji Abarai", "type": "Baboon-Snake", "desc": "Zabimaru is a segmented blade that extends as a whip in Shikai. In Bankai, Soo Zabimaru creates a massive skeletal snake form with devastating crushing power. It represents the beast within Renji.", "ability": "Hihio Zabimaru, Bankai: Soo Zabimaru"},
    {"name": "Nozarashi", "owner": "Kenpachi Zaraki", "type": "Constant Release", "desc": "Nozarashi is a massive axe-like blade that channels Kenpachi's immense power. Its Bankai greatly increases his size and power, turning him into a primal berserker. The name means 'weather-beaten one.'", "ability": "Bankai: Shitenshi no Nozarashi"},
    {"name": "Kyoka Suigetsu", "owner": "Sosuke Aizen", "type": "Illusion", "desc": "Kyoka Suigetsu has the ultimate hypnotic ability — complete hypnosis. Anyone who sees its release is trapped in perfect illusions controlled by Aizen. Considered the most dangerous zanpakuto ability in all of Soul Society.", "ability": "Complete Hypnosis (Shikai)"},
    {"name": "Sode no Shirayuki", "owner": "Rukia Kuchiki", "type": "Ice", "desc": "Sode no Shirayuki is a beautiful all-white ice-type zanpakuto with a white ribbon. Its dances include Tsukishiro (freezing), Hakuren (blizzard), and Bankai: Hakka no Togame (absolute zero freezing). Elegant and deadly.", "ability": "Some no Mai: Tsukishiro, Hakuren, Bankai: Hakka no Togame"},
    {"name": "Katen Kyokotsu", "owner": "Shunsui Kyoraku", "type": "Dual Blade", "desc": "Katen Kyokotsu consists of two blades that create children's games in Shikai — both participants must follow the rules. Bankai creates a tragic theatrical play. One of the oldest and most unique zanpakuto.", "ability": "Takaoni, Irooni, Darumasan, Bankai: Karamatsu Shinju"},
    {"name": "Sogyo no Kotowari", "owner": "Jushiro Ukitake", "type": "Dual Blade", "desc": "Sogyo no Kotowari consists of two blades connected by a cord that can absorb and redirect enemy energy attacks. Its ability represents the balance and duality of all things. A defensive masterwork.", "ability": "Energy Absorption & Redirection"},
    {"name": "Shinso", "owner": "Gin Ichimaru", "type": "Extension", "desc": "Shinso extends at incredible speed, piercing opponents before they can react. Its Bankai, Kamishini no Yari, extends at Mach 500 with deadly poison ability hidden in its blade. Gin's deceptive weapon.", "ability": "Bankai: Kamishini no Yari, Buto"}
]

# ============================================================
# STORY ARCS DATA
# ============================================================
ARCS = [
    {
        "name": "Agent of the Shinigami",
        "eps": "Episodes 1-20",
        "desc": "Ichigo Kurosaki's ordinary life changes forever when he meets Rukia Kuchiki, a Soul Reaper. After gaining Soul Reaper powers, Ichigo must protect his town from Hollows while learning to control his new abilities.",
        "key_events": "Meeting Rukia, first Hollow battles, introduction of Orihime, Uryu, and Chad, Grand Fisher encounter"
    },
    {
        "name": "Soul Society",
        "eps": "Episodes 21-63",
        "desc": "Ichigo and friends infiltrate Soul Society to rescue Rukia from her execution. They face the powerful Gotei 13 captains in an arc that reveals deep conspiracies and introduces the complex politics of Soul Society.",
        "key_events": "Souketsu Gate invasion, Byakuya vs Ichigo, Aizen's fake death, Rukia's execution rescue, Aizen's betrayal revealed"
    },
    {
        "name": "Arrancar",
        "eps": "Episodes 64-167",
        "desc": "Aizen's Arrancar army poses a new threat as Hollow-Soul Reaper hybrids attack Karakura Town. Ichigo trains to master his Hollow powers while the Gotei 13 prepares for war against the Espada.",
        "key_events": "Ulquiorra and Grimmjow's assault, Ichigo's Vizard training, battle for Karakura, FKT arc, Aizen's transcendence"
    },
    {
        "name": "The Lost Agent",
        "eps": "Episodes 168-229",
        "desc": "After losing his Soul Reaper powers, Ichigo' struggles with a normal life. A mysterious organization called Xcution offers to restore his powers through Fullbring, but their true motives are far darker.",
        "key_events": "Ichigo's power loss, Ginjo's betrayal, Fullbring training, Tsukishima's Book of the End, Ichigo's powers restored"
    },
    {
        "name": "Thousand-Year Blood War",
        "eps": "Episodes 230-366+",
        "desc": "The Quincy King Yhwach declares war on Soul Society, leading the Wandenreich in an invasion. This final arc reveals ancient history and tests every Soul Reaper to their absolute limit.",
        "key_events": "First Quincy invasion, Yamamoto's death, Ichigo's true heritage, Zero Division training, final battle against Yhwach"
    }
]

# ============================================================
# HTML TEMPLATE HELPERS
# ============================================================

def head(title, desc=None, canonical=None, og_image=None):
    d = desc or SITE_DESC
    img = og_image or f"https://{DOMAIN}/images/ichigo-kurosaki.png"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | {SITE_NAME}</title>
    <meta name="description" content="{d}">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>tailwind.config={{theme:{{extend:{{colors:{{accent:'{ACCENT}',accentLight:'{ACCENT_LIGHT}'}}}}}}}}</script>
    <link rel="canonical" href="https://{DOMAIN}{canonical or '/'}">
    <meta property="og:title" content="{title} | {SITE_NAME}">
    <meta property="og:description" content="{d}">
    <meta property="og:image" content="{img}">
    <meta property="og:url" content="https://{DOMAIN}{canonical or '/'}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="robots" content="index, follow">
    <link rel="icon" type="image/png" href="/favicon.png">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE}" crossorigin="anonymous"></script>
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA4}"></script>
    <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA4}');</script>
    <script type="application/ld+json">{{
    "@context":"https://schema.org",
    "@type":"WebSite",
    "name":"{SITE_NAME}",
    "url":"https://{DOMAIN}",
    "description":"{d}"
    }}</script>
</head>
<body class="bg-[{BG_DARK}] text-gray-200 font-sans flex flex-col min-h-screen">"""

NAV = f"""<nav class="bg-[{BG_NAV}] border-b border-gray-800 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <a href="/" class="text-2xl font-bold text-[{ACCENT}]">Bleach Wiki</a>
        <div class="hidden md:flex space-x-6 text-sm">
            <a href="/" class="hover:text-[{ACCENT}] transition">Home</a>
            <a href="/guides/characters/" class="hover:text-[{ACCENT}] transition">Characters</a>
            <a href="/guides/zanpakuto/" class="hover:text-[{ACCENT}] transition">Zanpakuto</a>
            <a href="/guides/arcs/" class="hover:text-[{ACCENT}] transition">Arcs</a>
            <a href="/about.html" class="hover:text-[{ACCENT}] transition">About</a>
            <a href="/contact.html" class="hover:text-[{ACCENT}] transition">Contact</a>
        </div>
        <button class="md:hidden text-gray-300" onclick="document.getElementById('mobileMenu').classList.toggle('hidden')">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>
    </div>
    <div id="mobileMenu" class="hidden md:hidden bg-[{BG_CARD}] border-t border-gray-800 px-4 py-3 space-y-2 text-sm">
        <a href="/" class="block py-1 hover:text-[{ACCENT}]">Home</a>
        <a href="/guides/characters/" class="block py-1 hover:text-[{ACCENT}]">Characters</a>
        <a href="/guides/zanpakuto/" class="block py-1 hover:text-[{ACCENT}]">Zanpakuto</a>
        <a href="/guides/arcs/" class="block py-1 hover:text-[{ACCENT}]">Arcs</a>
        <a href="/about.html" class="block py-1 hover:text-[{ACCENT}]">About</a>
        <a href="/contact.html" class="block py-1 hover:text-[{ACCENT}]">Contact</a>
    </div>
</nav>"""

FOOTER = f"""<footer class="bg-gray-900 text-gray-400 py-12 mt-auto">
    <div class="max-w-7xl mx-auto px-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
                <h3 class="text-white font-bold mb-3">Bleach Wiki</h3>
                <p class="text-sm">Your ultimate guide to the Bleach universe — character profiles, Zanpakuto guides, story arcs, Soul Society lore, and more.</p>
            </div>
            <div>
                <h3 class="text-white font-bold mb-3">Quick Links</h3>
                <ul class="space-y-2 text-sm">
                    <li><a href="/guides/characters/" class="hover:text-[{ACCENT}] transition">Characters</a></li>
                    <li><a href="/guides/zanpakuto/" class="hover:text-[{ACCENT}] transition">Zanpakuto</a></li>
                    <li><a href="/guides/arcs/" class="hover:text-[{ACCENT}] transition">Story Arcs</a></li>
                    <li><a href="/sitemap.html" class="hover:text-[{ACCENT}] transition">Sitemap</a></li>
                </ul>
            </div>
            <div>
                <h3 class="text-white font-bold mb-3">Support</h3>
                <ul class="space-y-2 text-sm">
                    <li><a href="/about.html" class="hover:text-[{ACCENT}] transition">About</a></li>
                    <li><a href="/contact.html" class="hover:text-[{ACCENT}] transition">Contact</a></li>
                    <li><a href="/privacy-policy.html" class="hover:text-[{ACCENT}] transition">Privacy Policy</a></li>
                    <li><a href="/terms.html" class="hover:text-[{ACCENT}] transition">Terms</a></li>
                    <li><a href="/cookie-policy.html" class="hover:text-[{ACCENT}] transition">Cookie Policy</a></li>
                </ul>
            </div>
        </div>
        <div class="mt-8 pt-8 border-t border-gray-800 text-sm text-center">
            <select onchange="if(this.value)window.open(this.value,'_blank')" class="bg-gray-800 text-gray-300 px-3 py-2 rounded text-sm border border-gray-700">
                <option value="">Our Sites</option>
                <option value="https://jycsd.com">Myers Media</option>
                <option value="https://healthy.jycsd.com">Daily Health</option>
                <option value="https://pets.jycsd.com">Pet Care</option>
                <option value="https://home.jycsd.com">Home & Garden</option>
                <option value="https://finance.jycsd.com">Personal Finance</option>
                <option value="https://tech.jycsd.com">Tech Reviews</option>
                <option value="https://travel.jycsd.com">Travel Guides</option>
            </select>
            <p class="mt-4">&copy; 2026 {SITE_NAME}. All rights reserved.</p>
        </div>
    </div>
</footer>
</body>
</html>"""

def make_page(title, content, desc=None, canonical=None, og_image=None):
    """Wrap content in full HTML page."""
    return head(title, desc, canonical, og_image) + NAV + content + "\n" + FOOTER


def char_card(slug, name, title_str):
    return f"""<a href="/guides/characters/{slug}.html" class="bg-[{BG_CARD}] rounded-lg overflow-hidden hover:ring-2 hover:ring-[{ACCENT}] transition-all duration-300">
    <div class="aspect-square bg-gray-800 relative overflow-hidden">
        <img src="/images/{slug}.png" alt="{name}" class="w-full h-full object-contain" loading="lazy" onerror="{ONERROR_SVG}">
    </div>
    <div class="p-4">
        <h3 class="font-bold text-lg text-white">{name}</h3>
        <p class="text-sm text-gray-400">{title_str}</p>
    </div>
</a>"""


def write_file(path, content):
    full = os.path.join(BASE_DIR, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Created: {path}")


# ============================================================
# PAGE GENERATORS
# ============================================================

def render_index():
    # Banner slides (first 6)
    banner_chars = CHARACTERS[:6]
    slides = []
    for i, c in enumerate(banner_chars):
        slides.append(f"""<div class="slide min-w-full h-full flex-shrink-0 relative">
    <img src="/images/{c['slug']}.png" alt="{c['name']}" class="w-full h-full object-contain" loading="lazy" onerror="{ONERROR_SVG}">
    <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-6">
        <h2 class="text-2xl font-bold text-white">{c['name']}</h2>
        <p class="text-gray-300">{c['title']}</p>
    </div>
</div>""")
    banner_html = "\n".join(slides)

    # Top Characters (12)
    top_chars = CHARACTERS[:12]
    top_grid = "\n".join([char_card(c['slug'], c['name'], c['title']) for c in top_chars])

    # Category cards
    cats = [
        ("Characters", "/guides/characters/", f"Meet all {len(CHARACTERS)} Bleach characters with detailed profiles, abilities, and backstories.", ACCENT),
        ("Zanpakuto", "/guides/zanpakuto/", "Explore the legendary zanpakuto — their forms, abilities, and Bankai releases.", "#8b5cf6"),
        ("Story Arcs", "/guides/arcs/", "Follow the complete Bleach story from Agent of the Shinigami to the Thousand-Year Blood War.", "#3b82f6"),
        ("Soul Society", "/guides/characters/", "Discover the Gotei 13 captains, divisions, and the intricate politics of Soul Society.", "#ef4444"),
    ]
    cat_imgs = ["ichigo-kurosaki", "byakuya-kuchiki", "rukia-kuchiki", "yamamoto-genryusai"]
    cat_cards = []
    for i, (name, link, desc, color) in enumerate(cats):
        ci = cat_imgs[i]
        cat_cards.append(f"""<a href="{link}" class="bg-[{BG_CARD}] rounded-lg overflow-hidden hover:ring-2 hover:ring-[{ACCENT}] transition-all duration-300">
    <div class="h-40 bg-gray-800 relative overflow-hidden">
        <img src="/images/{ci}.png" alt="{name}" class="w-full h-full object-contain" loading="lazy" onerror="{ONERROR_SVG}">
    </div>
    <div class="p-4">
        <div class="w-12 h-12 rounded-full flex items-center justify-center mb-3" style="background-color:{color}20; border: 2px solid {color}">
            <span class="text-xl font-bold" style="color:{color}">{name[0]}</span>
        </div>
        <h3 class="text-xl font-bold text-white mb-2">{name}</h3>
        <p class="text-gray-400 text-sm">{desc}</p>
        <span class="text-[{ACCENT}] text-sm mt-3 inline-block">Explore More &rarr;</span>
    </div>
</a>""")
    cat_html = "\n".join(cat_cards)

    # Popular Topics
    pop_topics = [
        ("Captain-Level Bankai Revealed", f"Explore the Bankai abilities of Gotei 13 captains — from Senbonzakura Kageyoshi to Zanka no Tachi. These ultimate techniques define the power ceiling of Soul Society.", "/guides/zanpakuto/"),
        ("The True History of Soul Society", f"Dive into the thousand-year history of Soul Society, from its founding by Yamamoto to the devastating Quincy invasion led by Yhwach.", "/guides/arcs/"),
        ("Espada Ranked by Power", f"From the Sexta to the Primera, discover the abilities and rankings of Aizen's elite Arrancar warriors and their devastating Resurreccion forms.", "/guides/characters/grimmjow-jaegerjaquez.html"),
    ]
    pop_html = "\n".join([
        f"""<div class="bg-[{BG_CARD}] rounded-lg overflow-hidden flex flex-col md:flex-row hover:ring-2 hover:ring-[{ACCENT}] transition-all duration-300">
    <div class="md:w-48 h-48 bg-gray-800 flex-shrink-0">
        <img src="/images/{img}.png" alt="{title}" class="w-full h-full object-contain" loading="lazy" onerror="{ONERROR_SVG}">
    </div>
    <div class="p-6 flex flex-col justify-center">
        <h3 class="text-xl font-bold text-white mb-2">{title}</h3>
        <p class="text-gray-400 text-sm mb-3">{desc}</p>
        <a href="{link}" class="text-[{ACCENT}] text-sm hover:underline">Read More &rarr;</a>
    </div>
</div>"""
        for title, desc, link, img in [
            ("Captain-Level Bankai Revealed", "Explore the Bankai abilities of Gotei 13 captains — from Senbonzakura Kageyoshi to Zanka no Tachi. These ultimate techniques define the power ceiling of Soul Society.", "/guides/zanpakuto/", "yamamoto-genryusai"),
            ("The True History of Soul Society", "Dive into the thousand-year history of Soul Society, from its founding by Yamamoto to the devastating Quincy invasion led by Yhwach.", "/guides/arcs/", "byakuya-kuchiki"),
            ("Espada Ranked by Power", "From the Sexta to the Primera, discover the abilities and rankings of Aizen's elite Arrancar warriors and their devastating Resurreccion forms.", "/guides/characters/ulquiorra-cifer.html", "ulquiorra-cifer"),
        ]
    ])

    content = f"""
<!-- Banner Carousel (CSS only) -->
<section class="w-full bg-[{BG_CARD}]">
    <div class="max-w-7xl mx-auto">
        <div class="carousel-container overflow-hidden relative" style="height:500px">
            <div class="carousel-track flex h-full animate-scroll">
                {banner_html}
            </div>
            <div class="absolute bottom-4 left-1/2 -translate-x-1/2 flex space-x-2 z-10">
                <div class="w-3 h-3 rounded-full bg-[{ACCENT}]"></div>
                <div class="w-3 h-3 rounded-full bg-gray-500"></div>
                <div class="w-3 h-3 rounded-full bg-gray-500"></div>
                <div class="w-3 h-3 rounded-full bg-gray-500"></div>
                <div class="w-3 h-3 rounded-full bg-gray-500"></div>
                <div class="w-3 h-3 rounded-full bg-gray-500"></div>
            </div>
        </div>
    </div>
</section>

<!-- Top Characters -->
<section class="w-full max-w-7xl mx-auto px-4 py-12">
    <div class="flex items-center justify-between mb-8">
        <h2 class="text-3xl font-bold text-white">Top Characters</h2>
        <a href="/guides/characters/" class="text-[{ACCENT}] hover:underline text-sm">View All &rarr;</a>
    </div>
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {top_grid}
    </div>
</section>

<!-- Explore Categories -->
<section class="w-full max-w-7xl mx-auto px-4 py-12">
    <h2 class="text-3xl font-bold text-white mb-8">Explore Categories</h2>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {cat_html}
    </div>
</section>

<!-- Popular Topics -->
<section class="w-full max-w-7xl mx-auto px-4 py-12">
    <h2 class="text-3xl font-bold text-white mb-8">Popular Topics</h2>
    <div class="space-y-6">
        {pop_html}
    </div>
</section>

<style>
@keyframes scrollBanner {{
    0% {{ transform: translateX(0); }}
    16.66% {{ transform: translateX(0); }}
    33.33% {{ transform: translateX(-100%); }}
    50% {{ transform: translateX(-100%); }}
    66.66% {{ transform: translateX(-200%); }}
    83.33% {{ transform: translateX(-200%); }}
    100% {{ transform: translateX(0); }}
}}
.carousel-track {{
    animation: scrollBanner 24s infinite;
}}
.carousel-container:hover .carousel-track {{
    animation-play-state: paused;
}}
</style>
"""
    return make_page("Home", content, canonical="/")


def render_static(filename, title, content_body):
    content = f"""<section class="w-full max-w-7xl mx-auto px-4 py-12">
    <div class="max-w-4xl mx-auto bg-[{BG_CARD}] rounded-lg p-8">
        <h1 class="text-3xl font-bold text-white mb-6">{title}</h1>
        <div class="prose prose-invert max-w-none text-gray-300 space-y-4">
            {content_body}
        </div>
    </div>
</section>"""
    return make_page(title, content, canonical=f"/{filename}.html")


def render_about():
    body = """
<p>Welcome to Bleach Wiki, your ultimate guide to the Bleach universe. We are dedicated to providing comprehensive information about the characters, zanpakuto, story arcs, and the rich lore of Soul Society.</p>
<p>Our mission is to create the most complete and accessible resource for both new fans and longtime followers of the Bleach series. Whether you are just starting the Agent of the Shinigami arc or revisiting the Thousand-Year Blood War, our guides are here to enhance your experience.</p>
<p>Bleach Wiki covers:</p>
<ul class="list-disc pl-6 space-y-2">
<li>Detailed profiles of every major character</li>
<li>In-depth analysis of zanpakuto and their abilities</li>
<li>Complete story arc breakdowns with key events</li>
<li>Exploration of Soul Society, Hueco Mundo, and the Human World</li>
<li>Trivia and behind-the-scenes information</li>
</ul>
<p>This site is created by fans, for fans. We strive for accuracy and depth in every article we publish. If you notice any errors or have suggestions for improvement, please contact us through our contact page.</p>
"""
    return render_static("about", "About Bleach Wiki", body)


def render_contact():
    body = """
<p>We would love to hear from you! Whether you have a question about the Bleach series, a suggestion for our wiki, or just want to share your thoughts, feel free to reach out.</p>
<p>You can contact us through the following channels:</p>
<ul class="list-disc pl-6 space-y-2">
<li>Email: contact@bleach.jycsd.com</li>
<li>Response time: 1-2 business days</li>
</ul>
<p>For corrections or content suggestions, please include relevant sources or references so we can verify and update our information accurately.</p>
"""
    return render_static("contact", "Contact Us", body)


def render_privacy():
    body = """
<p>At Bleach Wiki, we take your privacy seriously. This Privacy Policy explains how we collect, use, and protect your personal information when you visit our website.</p>
<h2 class="text-xl font-bold text-white mt-6 mb-3">Information We Collect</h2>
<p>We use Google Analytics (GA4) to understand how visitors interact with our site. This collects anonymized data such as page views, session duration, and browser information. We do not collect personally identifiable information unless you voluntarily provide it through our contact form.</p>
<h2 class="text-xl font-bold text-white mt-6 mb-3">Cookies</h2>
<p>We use minimal cookies for analytics purposes. Google Analytics uses cookies to distinguish unique users and track session information. You can opt out of Google Analytics cookies by installing the Google Analytics opt-out browser add-on.</p>
<h2 class="text-xl font-bold text-white mt-6 mb-3">Advertising on Our Site</h2>
<p>We display advertisements through Google AdSense. Google may use cookies to serve personalized ads based on your browsing history. You can manage your ad personalization settings through your Google Account.</p>
<h2 class="text-xl font-bold text-white mt-6 mb-3">Third-Party Services</h2>
<p>We use the following third-party services: Google Analytics (analytics), Google AdSense (advertising), and Tailwind CSS (styling). Each service has its own privacy policy governing data handling.</p>
<h2 class="text-xl font-bold text-white mt-6 mb-3">Your Rights</h2>
<p>You have the right to request access to, correction of, or deletion of your personal data. To exercise these rights, please contact us.</p>
"""
    return render_static("privacy-policy", "Privacy Policy", body)


def render_terms():
    body = """
<p>By using Bleach Wiki, you agree to the following terms and conditions. Please read them carefully.</p>
<h2 class="text-xl font-bold text-white mt-6 mb-3">Content Usage</h2>
<p>All content on this website is provided for informational and entertainment purposes. While we strive for accuracy, we make no guarantees regarding the completeness or reliability of the information presented.</p>
<h2 class="text-xl font-bold text-white mt-6 mb-3">Intellectual Property</h2>
<p>Bleach is a trademark of Tite Kubo and Shueisha. This fan wiki is not affiliated with or endorsed by the official rights holders. All character images and references are used under fair use for informational purposes.</p>
<h2 class="text-xl font-bold text-white mt-6 mb-3">User Conduct</h2>
<p>Users agree not to use this site for any unlawful purpose or in any way that could damage, disable, or impair the website. We reserve the right to block access to users who violate these terms.</p>
<h2 class="text-xl font-bold text-white mt-6 mb-3">Limitation of Liability</h2>
<p>Bleach Wiki and its operators shall not be liable for any damages arising from the use of or inability to use this website, including but not limited to direct, indirect, incidental, or consequential damages.</p>
"""
    return render_static("terms", "Terms of Service", body)


def render_cookie():
    body = """
<p>This Cookie Policy explains what cookies are and how we use them on Bleach Wiki.</p>
<h2 class="text-xl font-bold text-white mt-6 mb-3">What Are Cookies</h2>
<p>Cookies are small text files stored on your device when you visit a website. They help websites remember your preferences and improve your browsing experience.</p>
<h2 class="text-xl font-bold text-white mt-6 mb-3">How We Use Cookies</h2>
<p>We use Google Analytics cookies to track page views and user interactions. This helps us understand which content is most popular and improve our site. These cookies are anonymized and do not identify you personally.</p>
<h2 class="text-xl font-bold text-white mt-6 mb-3">Managing Cookies</h2>
<p>Most web browsers allow you to control cookies through your settings. You can choose to block all cookies, delete existing cookies, or receive a notification when a cookie is set. Note that blocking some cookies may affect website functionality.</p>
<h2 class="text-xl font-bold text-white mt-6 mb-3">Third-Party Cookies</h2>
<p>Google AdSense may use cookies for ad personalization. You can opt out of personalized advertising by visiting Google's Ad Settings page.</p>
"""
    return render_static("cookie-policy", "Cookie Policy", body)


def render_char_index():
    grid = "\n".join([char_card(c['slug'], c['name'], c['title']) for c in CHARACTERS])
    content = f"""<section class="w-full max-w-7xl mx-auto px-4 py-12">
    <h1 class="text-4xl font-bold text-white mb-4">All Characters</h1>
    <p class="text-gray-400 mb-8">Complete list of characters from the Bleach universe. Click any character to view their full profile.</p>
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {grid}
    </div>
</section>"""
    return make_page("Characters", content, "Complete list of Bleach characters with detailed profiles.", canonical="/guides/characters/")


def render_char_detail(c, related_html=""):
    content = f"""<section class="w-full max-w-7xl mx-auto px-4 py-12">
    <div class="max-w-5xl mx-auto">
        <nav class="text-sm text-gray-400 mb-6">
            <a href="/" class="hover:text-[{ACCENT}]">Home</a> &raquo;
            <a href="/guides/characters/" class="hover:text-[{ACCENT}]">Characters</a> &raquo;
            <span class="text-white">{c['name']}</span>
        </nav>

        <div class="bg-[{BG_CARD}] rounded-lg overflow-hidden mb-8">
            <div class="flex flex-col md:flex-row">
                <div class="md:w-96 h-96 bg-gray-800 flex-shrink-0">
                    <img src="../../images/{c['slug']}.png" alt="{c['name']}" class="w-full h-full object-contain" onerror="{ONERROR_SVG}">
                </div>
                <div class="p-8 flex flex-col justify-center">
                    <h1 class="text-4xl font-bold text-white mb-2">{c['name']}</h1>
                    <p class="text-[{ACCENT}] text-lg mb-4">{c['title']}</p>
                    <div class="space-y-2 text-sm text-gray-400">
                        <p><span class="text-gray-300 font-semibold">Affiliation:</span> {c['affiliation']}</p>
                        <p><span class="text-gray-300 font-semibold">Rank:</span> {c['rank']}</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="space-y-6">
            <div class="bg-[{BG_CARD}] rounded-lg p-6">
                <h2 class="text-2xl font-bold text-white mb-3">Overview</h2>
                <p class="text-gray-300 leading-relaxed">{c['overview']}</p>
            </div>
            <div class="bg-[{BG_CARD}] rounded-lg p-6">
                <h2 class="text-2xl font-bold text-white mb-3">Appearance</h2>
                <p class="text-gray-300 leading-relaxed">{c['appearance']}</p>
            </div>
            <div class="bg-[{BG_CARD}] rounded-lg p-6">
                <h2 class="text-2xl font-bold text-white mb-3">Personality</h2>
                <p class="text-gray-300 leading-relaxed">{c['personality']}</p>
            </div>
            <div class="bg-[{BG_CARD}] rounded-lg p-6">
                <h2 class="text-2xl font-bold text-white mb-3">Abilities</h2>
                <p class="text-gray-300 leading-relaxed">{c['abilities']}</p>
            </div>
            <div class="bg-[{BG_CARD}] rounded-lg p-6">
                <h2 class="text-2xl font-bold text-white mb-3">Trivia</h2>
                <p class="text-gray-300 leading-relaxed">{c['trivia']}</p>
            </div>
        </div>

        {related_html}

        <div class="mt-8 text-center">
            <a href="/guides/characters/" class="inline-block bg-[{ACCENT}] text-black font-bold px-6 py-3 rounded-lg hover:bg-[{ACCENT_LIGHT}] transition">&larr; Back to All Characters</a>
        </div>
    </div>
</section>"""
    return make_page(c['name'], content, f"Learn everything about {c['name']} — {c['title']} from Bleach.", canonical=f"/guides/characters/{c['slug']}.html", og_image=f"https://{DOMAIN}/images/{c['slug']}.png")


def render_char_detail_related(c_index):
    """Render related characters section for a character detail page."""
    # Show 4 related characters
    n = len(CHARACTERS)
    related = []
    for offset in [1, 2, 3, 4]:
        idx = (c_index + offset) % n
        rc = CHARACTERS[idx]
        related.append(char_card(rc['slug'], rc['name'], rc['title']))
    grid = "\n".join(related)
    return f"""<section class="w-full max-w-7xl mx-auto px-4 py-8">
    <h2 class="text-2xl font-bold text-white mb-6">Related Characters</h2>
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {grid}
    </div>
</section>"""


def render_zanpakuto_index():
    cards = []
    for z in ZANPAKUTO:
        # Find the owner character slug
        owner_slug = None
        for c in CHARACTERS:
            if c['name'].lower().startswith(z['owner'].lower().split()[-1]) or z['owner'].lower() in c['name'].lower():
                # Fuzzy match by last name
                if z['owner'].split()[-1].lower() in c['name'].lower():
                    owner_slug = c['slug']
                    break
        if not owner_slug:
            owner_slug = CHARACTERS[0]['slug']
        cards.append(f"""<div class="bg[{BG_CARD}] rounded-lg overflow-hidden hover:ring-2 hover:ring-[{ACCENT}] transition-all duration-300">
    <div class="aspect-square bg-gray-800 relative overflow-hidden">
        <img src="/images/{owner_slug}.png" alt="{z['name']}" class="w-full h-full object-contain" loading="lazy" onerror="{ONERROR_SVG}">
        <div class="absolute top-2 right-2 bg-[{ACCENT}] text-black text-xs font-bold px-2 py-1 rounded">{z['type']}</div>
    </div>
    <div class="p-4">
        <h3 class="font-bold text-lg text-white">{z['name']}</h3>
        <p class="text-sm text-[{ACCENT}] mb-2">Wielder: {z['owner']}</p>
        <p class="text-gray-400 text-sm mb-3">{z['desc']}</p>
        <p class="text-gray-500 text-xs"><span class="text-gray-400 font-semibold">Abilities:</span> {z['ability']}</p>
    </div>
</div>""")

    content = f"""<section class="w-full max-w-7xl mx-auto px-4 py-12">
    <h1 class="text-4xl font-bold text-white mb-4">Zanpakuto</h1>
    <p class="text-gray-400 mb-8">Explore the legendary zanpakuto of Bleach — their forms, abilities, and Bankai releases. Each zanpakuto is a reflection of its wielder's soul.</p>
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {''.join(cards)}
    </div>
</section>"""
    return make_page("Zanpakuto", content, "Complete guide to Bleach Zanpakuto — legendary swords and their Bankai abilities.", canonical="/guides/zanpakuto/")


def render_arcs_index():
    cards = []
    for i, a in enumerate(ARCS):
        img_slug = CHARACTERS[i]['slug']
        cards.append(f"""<div class="bg[{BG_CARD}] rounded-lg overflow-hidden hover:ring-2 hover:ring-[{ACCENT}] transition-all duration-300">
    <div class="aspect-video bg-gray-800 relative overflow-hidden">
        <img src="/images/{img_slug}.png" alt="{a['name']}" class="w-full h-full object-contain" loading="lazy" onerror="{ONERROR_SVG}">
        <div class="absolute top-2 right-2 bg-[{ACCENT}] text-black text-xs font-bold px-2 py-1 rounded">{a['eps']}</div>
    </div>
    <div class="p-4">
        <h3 class="font-bold text-lg text-white">{a['name']}</h3>
        <p class="text-gray-400 text-sm mb-3">{a['desc']}</p>
        <details class="text-sm">
            <summary class="text-[{ACCENT}] cursor-pointer">Key Events</summary>
            <p class="text-gray-500 mt-2">{a['key_events']}</p>
        </details>
    </div>
</div>""")

    content = f"""<section class="w-full max-w-7xl mx-auto px-4 py-12">
    <h1 class="text-4xl font-bold text-white mb-4">Story Arcs</h1>
    <p class="text-gray-400 mb-8">Follow the complete Bleach storyline through its major arcs, from the beginning to the epic conclusion.</p>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {''.join(cards)}
    </div>
</section>"""
    return make_page("Story Arcs", content, "Complete guide to Bleach story arcs — from Agent of the Shinigami to Thousand-Year Blood War.", canonical="/guides/arcs/")


def render_sitemap():
    links = [
        ("/", "Home"),
        ("/about.html", "About"),
        ("/contact.html", "Contact"),
        ("/privacy-policy.html", "Privacy Policy"),
        ("/terms.html", "Terms of Service"),
        ("/cookie-policy.html", "Cookie Policy"),
        ("/guides/characters/", "All Characters"),
    ]
    for c in CHARACTERS:
        links.append((f"/guides/characters/{c['slug']}.html", c['name']))
    links.append(("/guides/zanpakuto/", "Zanpakuto"))
    links.append(("/guides/arcs/", "Story Arcs"))

    items = "\n".join([f'<li><a href="{url}" class="hover:text-[{ACCENT}] transition">{name}</a></li>' for url, name in links])
    content = f"""<section class="w-full max-w-7xl mx-auto px-4 py-12">
    <div class="max-w-4xl mx-auto bg-[{BG_CARD}] rounded-lg p-8">
        <h1 class="text-3xl font-bold text-white mb-6">Sitemap</h1>
        <ul class="space-y-2 text-gray-300">
            {items}
        </ul>
    </div>
</section>"""
    return make_page("Sitemap", content, canonical="/sitemap.html")


# ============================================================
# MAIN
# ============================================================
def main():
    print("Rendering Bleach Wiki...")

    # Static pages
    print("\n[Static Pages]")
    for fn, render_fn in [
        ("index.html", render_index),
        ("about.html", render_about),
        ("contact.html", render_contact),
        ("privacy-policy.html", render_privacy),
        ("terms.html", render_terms),
        ("cookie-policy.html", render_cookie),
        ("sitemap.html", render_sitemap),
    ]:
        write_file(fn, render_fn())

    # Character index
    print("\n[Character Index]")
    write_file("guides/characters/index.html", render_char_index())

    # Character detail pages
    print("\n[Character Details]")
    n = len(CHARACTERS)
    for i, c in enumerate(CHARACTERS):
        related = render_char_detail_related(i)
        write_file(f"guides/characters/{c['slug']}.html", render_char_detail(c, related))

    # Zanpakuto index
    print("\n[Zanpakuto Index]")
    write_file("guides/zanpakuto/index.html", render_zanpakuto_index())

    # Story arcs index
    print("\n[Story Arcs Index]")
    write_file("guides/arcs/index.html", render_arcs_index())

    print(f"\n{'='*50}")
    print("Rendering complete!")


if __name__ == "__main__":
    main()
