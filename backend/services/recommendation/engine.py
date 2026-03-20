"""
3D Hashmap: haircut_db[FaceShape][FacialFeatureProfile][SkinType]
→ list of HaircutObject

FacialFeatureProfile is a string key derived from the three extracted features.
We use a "primary feature" collapse: the most dominant feature drives the profile.
"""
from typing import Optional

# ── Haircut Object Schema ─────────────────────────────────────────────────────

def haircut(
    name: str,
    length: str,          # short | medium | long
    maintenance: str,     # high | low
    barber_instructions: str,
    styling_products: list[str],
    avoid_if: list[str],
    description: str,
) -> dict:
    return {
        "name": name,
        "length": length,
        "maintenance": maintenance,
        "barber_instructions": barber_instructions,
        "styling_products": styling_products,
        "avoid_if": avoid_if,
        "description": description,
    }


# ── Haircut Database ──────────────────────────────────────────────────────────

_HAIRCUTS = {
    "oval": {
        "strong": {
            "oily":        [
                haircut("Classic Taper", "short", "low",
                        "Taper the sides with a 2-guard fading to skin, keep 2-3 inches on top, textured crop.",
                        ["Matt clay", "Sea salt spray"],
                        ["Very oily scalp without absorbent product"],
                        "A timeless taper that works with oval faces and strong jaws."),
                haircut("French Crop", "short", "low",
                        "Scissor cut on top, 1.5 inches, blunt fringe at brow level, tapered sides.",
                        ["Light matte paste"],
                        ["Receding hairline"],
                        "Clean and low fuss; the fringe balances a strong jaw."),
                haircut("Slicked-Back Undercut", "medium", "high",
                        "Disconnect undercut at temples, leave 4+ inches on top, train hair straight back.",
                        ["Pomade", "Blow dryer"],
                        ["Fine/thinning hair"],
                        "Emphasises a strong jaw with a sleek, powerful look."),
            ],
            "dry":         [
                haircut("Textured Quiff", "medium", "high",
                        "Fade sides to 1-guard, leave 3-4 inches on top, point-cut for texture.",
                        ["Moisturising pomade", "Hair oil"],
                        ["Very fine hair"],
                        "Adds height and texture; moisturising products combat dryness."),
                haircut("Buzz Cut", "short", "low",
                        "Uniform 2-guard all over, optional skin fade at hairline.",
                        ["SPF scalp moisturiser"],
                        ["Scalp sensitivity to sun"],
                        "Minimal and clean; easy to manage with dry hair."),
            ],
            "combination": [
                haircut("Mid-Fade Crop", "short", "low",
                        "Mid skin fade on sides, textured crop on top, light fringe.",
                        ["Matt clay", "Lightweight mousse"],
                        ["Curly hair unless re-styled"],
                        "Versatile cut that suits combination skin because it keeps scalp exposure balanced."),
            ],
            "normal":      [
                haircut("Classic Side Part", "medium", "high",
                        "Hard part on left or right, scissor blended sides, 3 inches on top combed sideways.",
                        ["Medium-hold pomade"],
                        [],
                        "A distinguished everyday style for oval faces with strong jaws."),
            ],
        },
        "average": {
            "oily":        [
                haircut("Ivy League", "medium", "high",
                        "Scissor-cut, 2-3 inches on top, short tapered sides, combed-over parted look.",
                        ["Light-hold gel", "Absorbent dry shampoo"],
                        [],
                        "Collegiate and clean; the part distracts from an oily scalp."),
            ],
            "dry":         [
                haircut("Modern Pompadour", "medium", "high",
                        "High fade sides, 4 inches on top, blow-dried upward and back.",
                        ["Volumising mousse", "Strong pomade", "Hair serum"],
                        ["Severe thinning at crown"],
                        "Adds dramatic volume to counteract dry, flat hair."),
            ],
            "combination": [
                haircut("Textured Fringe", "medium", "low",
                        "Keep 2.5 inches on top, point-cut fringe to eyebrow line, light fade on sides.",
                        ["Sea salt spray", "Defining cream"],
                        [],
                        "Easygoing and flattering; works well for oval faces with average features."),
            ],
            "normal":      [
                haircut("The Flow", "long", "low",
                        "Grow all sides uniformly, shape neckline, layers at shoulder length.",
                        ["Hydrating conditioner", "Curl-defining cream if wavy"],
                        ["Very oily scalp"],
                        "A relaxed, long style that suits well-balanced oval faces."),
            ],
        },
        "soft": {
            "oily":        [
                haircut("Short Textured Crop", "short", "low",
                        "Crop the top to 1.5 inches, slight skin fade sides, broken-up texture on top.",
                        ["Matt clay", "Dry shampoo"],
                        [],
                        "Short enough to minimise scalp oil, texture adds definition to soft features."),
            ],
            "dry":         [
                haircut("Wavy Curtains", "medium", "low",
                        "Grow top to 3-4 inches, part in the middle, allow natural wave/movement.",
                        ["Leave-in conditioner", "Lightweight oil"],
                        ["Straight hair without wave"],
                        "The wave adds texture to soft features; conditioning products fix dryness."),
            ],
            "combination": [
                haircut("Shaggy Layered Cut", "medium", "low",
                        "Layered all over, razor-cut ends for movement, minimal fade on sides.",
                        ["Texturising spray", "Light wax"],
                        [],
                        "Relaxed and effortless on soft-featured oval faces."),
            ],
            "normal":      [
                haircut("Classic Caesar", "short", "low",
                        "1-2 inches on top, horizontal fringe, tapered sides.",
                        ["Light gel"],
                        [],
                        "A reliable short style for oval faces with softer features."),
            ],
        },
    },

    "square": {
        "strong": {
            "oily":        [
                haircut("Faux Hawk", "medium", "high",
                        "Skin fade sides, leave 3 inches on top, style into a central ridge without full hawk.",
                        ["Strong pomade", "Hairspray"],
                        ["Fine hair that won't hold volume"],
                        "Adds height to soften the square silhouette while showcasing a strong jaw."),
            ],
            "dry":         [
                haircut("Textured Brush-Up", "medium", "high",
                        "Fade sides to 2-guard, 3-4 inches on top, blow-dry upward and forward.",
                        ["Volumising cream", "Shine spray"],
                        [],
                        "Upward volume rounds off the square corners attractively."),
            ],
            "combination": [
                haircut("Quiff Fade", "medium", "high",
                        "High skin fade, 3-4 inches on top, blown back into a quiff.",
                        ["Pomade", "Blow dryer"],
                        [],
                        "Classic quiff that softens square edges with height at the front."),
            ],
            "normal":      [
                haircut("Crew Cut", "short", "low",
                        "Short all over with a slight taper, slightly longer at the front.",
                        ["Light gel or nothing"],
                        [],
                        "Emphasises strong masculine features on square faces."),
            ],
        },
        "average": {
            "oily":        [
                haircut("Disconnected Undercut", "medium", "high",
                        "Hard disconnection at temples, 4 inches on top, comb over or back.",
                        ["Pomade", "Dry shampoo for scalp"],
                        ["Very fine hair"],
                        "The volume on top contrasts and softens a wide square jaw."),
            ],
            "dry":         [
                haircut("Soft Pompadour", "medium", "high",
                        "Taper sides, 4 inches on top, blowdry voluminous pomp with curved rise.",
                        ["Moisturising pomade", "Thermal protectant"],
                        [],
                        "Rounded pompadour shape softens square angles."),
            ],
            "combination": [
                haircut("Side Swept Fringe", "medium", "high",
                        "Fade sides, grow fringe to 2.5 inches, sweep diagonally across forehead.",
                        ["Medium-hold cream"],
                        [],
                        "Diagonal fringe breaks the symmetry of square face angles."),
            ],
            "normal":      [
                haircut("Ivy League", "medium", "high",
                        "2-3 inches on top, side-parted, scissor-blended sides.",
                        ["Light pomade"],
                        [],
                        "Soft side part works beautifully on square faces."),
            ],
        },
        "soft": {
            "oily":        [
                haircut("Buzz Cut", "short", "low",
                        "Uniform grade 3 or 4 all over.",
                        ["SPF moisturiser"],
                        [],
                        "Very clean, balanced look for square faces."),
            ],
            "dry":         [
                haircut("Long Top Medium Fade", "medium", "low",
                        "Medium fade sides, 3+ inches on top, natural movement.",
                        ["Hydrating pomade", "Hair oil"],
                        [],
                        "Soft styling adds lightness to a square-soft combination."),
            ],
            "combination": [
                haircut("Natural Textured Top", "short", "low",
                        "Short fade sides, 1.5-2 inches on top, natural product-free texture.",
                        ["Sea salt spray (optional)"],
                        [],
                        "Low-effort look that balances square geometry with soft features."),
            ],
            "normal":      [
                haircut("Modern Caesar", "short", "low",
                        "1-2 inches all over, fringe forward, skin fade sides.",
                        ["Light clay"],
                        [],
                        "Clean look that suits square faces with softer features."),
            ],
        },
    },

    "round": {
        "strong": {
            "oily":        [
                haircut("High Top Fade", "medium", "high",
                        "High skin fade, 3-4 inches on flat top, squared off.",
                        ["Pomade", "Edge control"],
                        ["Soft, limp hair without volume"],
                        "Flat top adds height and length to counterbalance a round face."),
            ],
            "dry":         [
                haircut("Mohawk Fade", "medium", "high",
                        "Skin fade sides, leave 3-inch mohawk strip, style upward.",
                        ["Strong hold gel", "Hairspray"],
                        ["Thinning hair"],
                        "Maximum height — elongates round face dramatically."),
            ],
            "combination": [
                haircut("Pompadour Fade", "medium", "high",
                        "High fade, 4-inch top, pompadour blow-dried upward-back.",
                        ["Strong pomade", "Blow dryer"],
                        [],
                        "Volume on top creates the illusion of a longer face."),
            ],
            "normal":      [
                haircut("Quiff", "medium", "high",
                        "Taper sides, 3-4 inches on top, blow dried upward and slightly back.",
                        ["Medium pomade"],
                        [],
                        "The signature haircut for elongating round faces."),
            ],
        },
        "average": {
            "oily":        [
                haircut("Textured Fringe Upward", "medium", "low",
                        "Fade sides, 2.5 inches on top, push fringe upward for height.",
                        ["Sea salt spray", "Matt clay"],
                        [],
                        "Natural height effect without heavy products for oily scalps."),
            ],
            "dry":         [
                haircut("Wavy Undercut", "medium", "high",
                        "Undercut sides, grow top to 4+ inches, allow wave to form naturally.",
                        ["Wave cream", "Leave-in conditioner"],
                        ["Straight hair without curl product"],
                        "Waves add dimension and visual length to round faces."),
            ],
            "combination": [
                haircut("Angular Fringe", "medium", "low",
                        "Scissor fade sides, angled fringe pointing left or right.",
                        ["Light wax"],
                        [],
                        "Angular fringe breaks the circular symmetry of a round face."),
            ],
            "normal":      [
                haircut("Long Sweep Back", "long", "low",
                        "Grow sides and top uniformly to 4+ inches, sweep back and behind ears.",
                        ["Defining cream", "Light oil"],
                        [],
                        "Length behind the ears elongates the face."),
            ],
        },
        "soft": {
            "oily":        [
                haircut("Mid Fade Short Crop", "short", "low",
                        "Mid skin fade, short textured crop, no fringe.",
                        ["Matt clay", "Dry shampoo"],
                        [],
                        "Keep top short but add texture to avoid emphasising roundness."),
            ],
            "dry":         [
                haircut("Curtains", "medium", "low",
                        "Part in the middle, grow to jaw length, sweep outward.",
                        ["Serum", "Leave-in conditioner"],
                        [],
                        "Curtains elongate the face and suit soft features with round face."),
            ],
            "combination": [
                haircut("Side Part Medium", "medium", "high",
                        "Hard side part, comb top sideways, medium taper sides.",
                        ["Medium pomade"],
                        [],
                        "The side part creates asymmetry that flatters round faces."),
            ],
            "normal":      [
                haircut("Bro Flow", "long", "low",
                        "Grow all over to 4-6 inches, part naturally or push back.",
                        ["Lightweight conditioner"],
                        [],
                        "Natural long growth elongates a round face softly."),
            ],
        },
    },

    "heart": {
        "strong": {
            "oily":        [
                haircut("Tapered Sides with Volume", "medium", "high",
                        "Light taper (no skin fade), 3 inches on top, volume at the sides to balance narrow chin.",
                        ["Volumising mousse", "Matt paste"],
                        [],
                        "Volume kept at sides fills out the narrow heart-shaped chin."),
            ],
            "dry":         [
                haircut("Textured Layers", "medium", "low",
                        "Layered cut, scissor blended sides, movement through the hair.",
                        ["Hydrating leave-in", "Texturising spray"],
                        [],
                        "Layers add width at the jaw line, balancing the heart shape."),
            ],
            "combination": [
                haircut("Side Swept Fringe", "medium", "high",
                        "Moderate taper, 3-inch fringe swept diagonally.",
                        ["Medium pomade"],
                        [],
                        "Diagonal lines from the fringe break the wide forehead."),
            ],
            "normal":      [
                haircut("Long Layers", "long", "low",
                        "Grow to shoulder length, add face-framing layers.",
                        ["Defining cream"],
                        [],
                        "Length and layers balance a wide forehead and pointed chin."),
            ],
        },
        "average": {
            "oily":        [
                haircut("Classic Taper", "short", "low",
                        "Standard taper, 2 inches on top, textured finish.",
                        ["Light clay", "Dry shampoo"],
                        [],
                        "Keeps everything neat; avoid tight fades that emphasise wide forehead."),
            ],
            "dry":         [
                haircut("Soft Pompadour", "medium", "high",
                        "Moderate fade, rounded pompadour on top.",
                        ["Moisturising pomade"],
                        ["Skin fade — can over-emphasise wide forehead"],
                        "The rounded shape softens a heart face's angles."),
            ],
            "combination": [
                haircut("Fringe Forward", "short", "low",
                        "Forward fringe to cover upper forehead, scissor cut sides.",
                        ["Light clay"],
                        [],
                        "Fringe camouflages the wide forehead of a heart face."),
            ],
            "normal":      [
                haircut("Wavy Mid Part", "medium", "low",
                        "Middle part, 3 inches on top, natural wave, scissor-blended sides.",
                        ["Sea salt spray"],
                        [],
                        "Middle part widens the lower face visually."),
            ],
        },
        "soft": {
            "oily":        [
                haircut("Short Textured Crop", "short", "low",
                        "1.5 inches on top, defined texture, mid fade.",
                        ["Matt paste", "Dry shampoo"],
                        [],
                        "Simple and clean for a heart-shaped face with soft features."),
            ],
            "dry":         [
                haircut("Natural Flow", "medium", "low",
                        "Grow to 3 inches, no product — let natural movement show.",
                        ["Hair oil", "Leave-in conditioner"],
                        [],
                        "Natural softness works beautifully with soft-featured heart faces."),
            ],
            "combination": [
                haircut("Curtains", "medium", "low",
                        "Middle part, hang on both sides, chin length.",
                        ["Lightweight serum"],
                        [],
                        "Curtains broaden the lower face and balance a heart shape perfectly."),
            ],
            "normal":      [
                haircut("Layered Medium", "medium", "low",
                        "Scissor cut with layers, natural taper sides.",
                        ["Defining cream"],
                        [],
                        "Effortless layers flatter a heart face's natural symmetry."),
            ],
        },
    },

    "oblong": {
        "strong": {
            "oily":        [
                haircut("Disconnected Undercut Wide", "medium", "high",
                        "Disconnected undercut, keep volume wide on the sides (not top).",
                        ["Volumising mousse", "Matte paste"],
                        [],
                        "Side volume is key for oblong faces — widens the silhouette."),
            ],
            "dry":         [
                haircut("Textured Wide Crop", "short", "low",
                        "Keep top at 1.5-2 inches, texture pushed to the sides, not up.",
                        ["Moisturising clay"],
                        [],
                        "Horizontal emphasis balances a long oblong face."),
            ],
            "combination": [
                haircut("Fringe Low", "short", "low",
                        "Low fringe at eyebrow level or below, scissor-blended sides.",
                        ["Light wax"],
                        [],
                        "A fringe shortens a long face; keep it horizontal."),
            ],
            "normal":      [
                haircut("Side Part Short", "short", "high",
                        "Hard part, combed sideways, minimal height on top.",
                        ["Light pomade"],
                        [],
                        "Horizontal styling helps balance an oblong face."),
            ],
        },
        "average": {
            "oily":        [
                haircut("Buzz with Faded Sides", "short", "low",
                        "Grade 3 on top, grade 1 fade on sides — keep width.",
                        ["SPF moisturiser"],
                        [],
                        "Keeps hair from adding unwanted height."),
            ],
            "dry":         [
                haircut("Wavy Side Part", "medium", "high",
                        "Side part, waves styled sideways for width.",
                        ["Wave cream", "Sea salt spray"],
                        [],
                        "Horizontal wave movement broadens an oblong face."),
            ],
            "combination": [
                haircut("Medium Shaggy Cut", "medium", "low",
                        "Shaggy layers all over, movement at sides.",
                        ["Texturising spray", "Light wax"],
                        [],
                        "The relaxed width of shag cuts suits oblong faces."),
            ],
            "normal":      [
                haircut("Bro Flow", "long", "low",
                        "Long even growth, natural movement sideways.",
                        ["Leave-in conditioner"],
                        [],
                        "Long hair is fine for oblong if it has width and movement."),
            ],
        },
        "soft": {
            "oily":        [
                haircut("Fringe Crop", "short", "low",
                        "1.5 inches on top with short fringe, mid fade.",
                        ["Matt clay"],
                        [],
                        "Fringe shortens apparent face length."),
            ],
            "dry":         [
                haircut("Natural Waves", "medium", "low",
                        "Grow to 3 inches, encourage natural wave sideways.",
                        ["Curl cream", "Leave-in conditioner"],
                        [],
                        "Natural wide wave balances an oblong face."),
            ],
            "combination": [
                haircut("Layered Shag", "medium", "low",
                        "Heavy layer throughout, wide movement.",
                        ["Texturising spray"],
                        [],
                        "Wide shag movement is ideal for long oblong faces."),
            ],
            "normal":      [
                haircut("Medium Length Natural", "medium", "low",
                        "Grow to 3-4 inches, no heavy product, natural movement.",
                        ["Light defining cream"],
                        [],
                        "Clean and balanced for a softer oblong face."),
            ],
        },
    },

    "diamond": {
        "strong": {
            "oily":        [
                haircut("Full Fringe Textured", "medium", "low",
                        "Full horizontal fringe at eyebrow, widen at temples, fade sides lightly.",
                        ["Matt clay", "Dry shampoo"],
                        [],
                        "Fringe broadens narrow forehead; keeping temples full broadens the widest point less."),
            ],
            "dry":         [
                haircut("Side Swept Volume", "medium", "high",
                        "Volume built on one side, swept across narrow forehead.",
                        ["Volumising mousse", "Pomade"],
                        [],
                        "Added width at forehead balances diamond face geometry."),
            ],
            "combination": [
                haircut("Soft Quiff", "medium", "high",
                        "Moderate fade, gentle quiff without excessive height.",
                        ["Medium hold cream"],
                        [],
                        "Adds width proportionally without over-emphasising cheekbones."),
            ],
            "normal":      [
                haircut("Classic Taper", "short", "low",
                        "Even taper all around, 2 inches on top.",
                        ["Light gel or clay"],
                        [],
                        "Balanced and neutral — doesn't emphasise any extreme."),
            ],
        },
        "average": {
            "oily":        [
                haircut("Short Textured Fringe", "short", "low",
                        "Short crop with forward-pushed fringe, mid fade.",
                        ["Matt paste"],
                        [],
                        "Fringe coverage balances a narrow diamond forehead."),
            ],
            "dry":         [
                haircut("Wavy Natural Top", "medium", "low",
                        "Grow to 3 inches, natural wave, scissor taper sides.",
                        ["Wave cream", "Serum"],
                        [],
                        "Natural volume at top and sides helps balance the diamond widths."),
            ],
            "combination": [
                haircut("Textured Layers Medium", "medium", "low",
                        "Layered medium length, movement on all sides.",
                        ["Sea salt spray", "Light cream"],
                        [],
                        "Layers distribute volume — ideal for diamond faces."),
            ],
            "normal":      [
                haircut("Medium Side Part", "medium", "high",
                        "Hard side part, combed sideways, moderate fade.",
                        ["Medium pomade"],
                        [],
                        "Side part creates an asymmetric balance on a diamond face."),
            ],
        },
        "soft": {
            "oily":        [
                haircut("Buzz Fringe", "short", "low",
                        "Short buzz with a small fringe kept forward.",
                        ["Light oil-free moisturiser"],
                        [],
                        "Clean minimalist look for soft-featured diamond faces."),
            ],
            "dry":         [
                haircut("Curtains Diamond", "medium", "low",
                        "Middle part, hang evenly on both sides to jaw.",
                        ["Hydrating leave-in", "Serum"],
                        [],
                        "Curtains add width to the narrow points of a diamond face."),
            ],
            "combination": [
                haircut("Natural Shaggy", "medium", "low",
                        "Relaxed layers, minimal taper, movement throughout.",
                        ["Texturising spray"],
                        [],
                        "Easy movement suits soft-featured diamond faces."),
            ],
            "normal":      [
                haircut("Layered Long", "long", "low",
                        "Grow to shoulder, face-framing layers, natural volume.",
                        ["Defining cream"],
                        [],
                        "Long layers with face-framing balance a diamond face beautifully."),
            ],
        },
    },
}


# ── Feature Profile Collapse ──────────────────────────────────────────────────

def _derive_feature_profile(facial_features: dict) -> str:
    """
    Collapses three feature dimensions to a single profile key.
    Priority: jawline > cheekbones > forehead
    """
    if not facial_features:
        return "average"

    jawline = facial_features.get("jawline", "average")
    cheekbones = facial_features.get("cheekbones", "average")

    if jawline == "strong":
        return "strong"
    if jawline == "soft" and cheekbones == "flat":
        return "soft"
    if cheekbones == "prominent":
        return "strong"
    if jawline == "soft":
        return "soft"
    return "average"


# ── Public Interface ──────────────────────────────────────────────────────────

def get_haircut_recommendations(
    face_shape: Optional[str],
    facial_features: Optional[dict],
    skin_type: Optional[str],
    maintenance: str,
    length: str,
) -> list[dict]:
    """
    Look up the 3D hashmap and filter by maintenance + length preference.
    Returns a list of matching HaircutObjects.
    """
    shape = (face_shape or "oval").lower()
    feature_profile = _derive_feature_profile(facial_features or {})
    skin = (skin_type or "normal").lower()

    # Graceful fallbacks along each dimension
    shape_db = _HAIRCUTS.get(shape, _HAIRCUTS["oval"])
    feature_db = shape_db.get(feature_profile, shape_db.get("average", {}))
    haircuts = feature_db.get(skin, feature_db.get("normal", []))

    # Filter by user preferences
    filtered = [
        h for h in haircuts
        if h["maintenance"] == maintenance and h["length"] == length
    ]

    # If exact match empty, relax length filter
    if not filtered:
        filtered = [h for h in haircuts if h["maintenance"] == maintenance]

    # If still empty, return all from this cell
    if not filtered:
        filtered = haircuts

    return filtered