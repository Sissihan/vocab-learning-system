"""
Seed database with demo roots, vocabulary, semantic links, and demo user.
Run: python scripts/seed_data.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal, init_db
from app.models import Root, RootWord, User, UserKnowledge, Vocabulary, WordSemanticLink
from app.services.embeddings import generate_embedding
from app.utils.auth import get_password_hash
from app.utils.json_helpers import dumps

ROOTS = [
    ("act", "do, drive", "Latin", 1),
    ("aud", "hear", "Latin", 1),
    ("bio", "life", "Greek", 1),
    ("cap", "take, hold", "Latin", 2),
    ("cent", "hundred", "Latin", 1),
    ("cred", "believe", "Latin", 2),
    ("dict", "say, speak", "Latin", 2),
    ("duc", "lead", "Latin", 2),
    ("fac", "make, do", "Latin", 2),
    ("form", "shape", "Latin", 1),
    ("graph", "write", "Greek", 2),
    ("ject", "throw", "Latin", 2),
    ("log", "word, study", "Greek", 2),
    ("man", "hand", "Latin", 2),
    ("mit", "send", "Latin", 2),
    ("mov", "move", "Latin", 2),
    ("ped", "foot", "Latin", 2),
    ("port", "carry", "Latin", 2),
    ("scrib", "write", "Latin", 2),
    ("spect", "look", "Latin", 2),
    ("struct", "build", "Latin", 3),
    ("tract", "pull", "Latin", 3),
    ("ven", "come", "Latin", 2),
    ("vis", "see", "Latin", 1),
    ("voc", "call, voice", "Latin", 2),
]

# (word, meaning, phonetic, difficulty, root_key)
VOCABULARY = [
    ("action", "the process of doing something", "/ˈækʃn/", 1, "act"),
    ("active", "engaging in physical activity", "/ˈæktɪv/", 1, "act"),
    ("actor", "a person who performs in plays", "/ˈæktər/", 1, "act"),
    ("react", "respond to something", "/riˈækt/", 2, "act"),
    ("transaction", "an instance of buying or selling", "/trænˈzækʃn/", 3, "act"),
    ("audience", "assembled spectators", "/ˈɔːdiəns/", 2, "aud"),
    ("audio", "sound, especially recorded", "/ˈɔːdioʊ/", 1, "aud"),
    ("auditorium", "a large hall for audiences", "/ˌɔːdɪˈtɔːriəm/", 3, "aud"),
    ("audit", "official inspection of accounts", "/ˈɔːdɪt/", 3, "aud"),
    ("biology", "study of living organisms", "/baɪˈɒlədʒi/", 2, "bio"),
    ("biography", "account of someone's life", "/baɪˈɒɡrəfi/", 2, "bio"),
    ("biosphere", "regions with life", "/ˈbaɪəsfɪər/", 3, "bio"),
    ("antibiotic", "substance that destroys bacteria", "/ˌæntibaɪˈɒtɪk/", 3, "bio"),
    ("capture", "take into possession", "/ˈkæptʃər/", 2, "cap"),
    ("capacity", "maximum amount possible", "/kəˈpæsəti/", 2, "cap"),
    ("capable", "having ability", "/ˈkeɪpəbl/", 2, "cap"),
    ("participate", "take part in", "/pɑːˈtɪsɪpeɪt/", 3, "cap"),
    ("percent", "in or for every hundred", "/pərˈsent/", 1, "cent"),
    ("century", "period of one hundred years", "/ˈsentʃəri/", 2, "cent"),
    ("centennial", "relating to a hundredth anniversary", "/senˈteniəl/", 3, "cent"),
    ("credit", "ability to obtain goods before payment", "/ˈkredɪt/", 2, "cred"),
    ("credible", "able to be believed", "/ˈkredəbl/", 2, "cred"),
    ("incredible", "impossible to believe", "/ɪnˈkredəbl/", 2, "cred"),
    ("credential", "qualification or achievement", "/krəˈdenʃl/", 3, "cred"),
    ("dictate", "state or order authoritatively", "/ˈdɪkteɪt/", 2, "dict"),
    ("dictionary", "book of words and meanings", "/ˈdɪkʃəneri/", 1, "dict"),
    ("predict", "say what will happen", "/prɪˈdɪkt/", 2, "dict"),
    ("verdict", "decision on issue in court", "/ˈvɜːrdɪkt/", 3, "dict"),
    ("conduct", "lead or guide", "/ˈkɒndʌkt/", 2, "duc"),
    ("produce", "make or manufacture", "/prəˈdjuːs/", 2, "duc"),
    ("deduce", "arrive at by reasoning", "/dɪˈdjuːs/", 3, "duc"),
    ("aqueduct", "channel for conveying water", "/ˈækwɪdʌkt/", 4, "duc"),
    ("factory", "building for manufacturing", "/ˈfæktəri/", 2, "fac"),
    ("manufacture", "make on large scale", "/ˌmænjuˈfæktʃər/", 3, "fac"),
    ("facilitate", "make easier", "/fəˈsɪlɪteɪt/", 3, "fac"),
    ("artifact", "object made by human craft", "/ˈɑːrtɪfækt/", 3, "fac"),
    ("form", "visible shape of something", "/fɔːrm/", 1, "form"),
    ("format", "way something is arranged", "/ˈfɔːrmæt/", 2, "form"),
    ("transform", "make a marked change", "/trænsˈfɔːrm/", 2, "form"),
    ("reform", "make changes to improve", "/rɪˈfɔːrm/", 2, "form"),
    ("graph", "diagram showing relation", "/ɡræf/", 1, "graph"),
    ("graphic", "relating to visual art", "/ˈɡræfɪk/", 2, "graph"),
    ("autograph", "signature of famous person", "/ˈɔːtəɡræf/", 2, "graph"),
    ("photograph", "picture made with camera", "/ˈfoʊtəɡræf/", 2, "graph"),
    ("project", "planned undertaking", "/ˈprɒdʒekt/", 2, "ject"),
    ("reject", "dismiss as inadequate", "/rɪˈdʒekt/", 2, "ject"),
    ("inject", "introduce with syringe", "/ɪnˈdʒekt/", 2, "ject"),
    ("objective", "not influenced by feelings", "/əbˈdʒektɪv/", 3, "ject"),
    ("logic", "reasoning conducted according to principles", "/ˈlɒdʒɪk/", 2, "log"),
    ("dialogue", "conversation between people", "/ˈdaɪəlɒɡ/", 2, "log"),
    ("catalog", "complete list of items", "/ˈkætəlɒɡ/", 2, "log"),
    ("apology", "regretful acknowledgment", "/əˈpɒlədʒi/", 2, "log"),
    ("manual", "relating to hands", "/ˈmænjuəl/", 2, "man"),
    ("manage", "be in charge of", "/ˈmænɪdʒ/", 1, "man"),
    ("manuscript", "book written by hand", "/ˈmænjuskrɪpt/", 3, "man"),
    ("manipulate", "handle skillfully", "/məˈnɪpjuleɪt/", 3, "man"),
    ("transmit", "cause to pass from one place to another", "/trænzˈmɪt/", 2, "mit"),
    ("submit", "present for judgment", "/səbˈmɪt/", 2, "mit"),
    ("permit", "give authorization", "/pərˈmɪt/", 2, "mit"),
    ("mission", "important assignment", "/ˈmɪʃn/", 2, "mit"),
    ("move", "go in specified direction", "/muːv/", 1, "mov"),
    ("movement", "act of changing position", "/ˈmuːvmənt/", 1, "mov"),
    ("remove", "take away from position", "/rɪˈmuːv/", 2, "mov"),
    ("mobile", "able to move freely", "/ˈmoʊbl/", 2, "mov"),
    ("pedal", "foot-operated lever", "/ˈpedl/", 2, "ped"),
    ("pedestrian", "person walking", "/pəˈdestriən/", 2, "ped"),
    ("expedition", "journey for particular purpose", "/ˌekspəˈdɪʃn/", 3, "ped"),
    ("biped", "two-footed animal", "/ˈbaɪped/", 3, "ped"),
    ("port", "harbor town", "/pɔːrt/", 1, "port"),
    ("portable", "able to be carried", "/ˈpɔːrtəbl/", 2, "port"),
    ("transport", "carry to place", "/trænsˈpɔːrt/", 2, "port"),
    ("export", "send goods to another country", "/ˈekspɔːrt/", 2, "port"),
    ("describe", "give account in words", "/dɪˈskraɪb/", 2, "scrib"),
    ("script", "written text of play", "/skrɪpt/", 2, "scrib"),
    ("prescription", "written order for medicine", "/prɪˈskrɪpʃn/", 3, "scrib"),
    ("subscribe", "arrange to receive regularly", "/səbˈskraɪb/", 3, "scrib"),
    ("spectator", "person who watches", "/ˈspekteɪtər/", 2, "spect"),
    ("inspect", "look at closely", "/ɪnˈspekt/", 2, "spect"),
    ("respect", "admiration felt for someone", "/rɪˈspekt/", 1, "spect"),
    ("perspective", "point of view", "/pərˈspektɪv/", 3, "spect"),
    ("structure", "arrangement of parts", "/ˈstrʌktʃər/", 2, "struct"),
    ("construct", "build or make", "/kənˈstrʌkt/", 2, "struct"),
    ("destruct", "destroy", "/dɪˈstrʌkt/", 3, "struct"),
    ("infrastructure", "basic physical systems", "/ˈɪnfrəstrʌktʃər/", 4, "struct"),
    ("tractor", "powerful motor vehicle", "/ˈtræktər/", 2, "tract"),
    ("attract", "cause to come to place", "/əˈtrækt/", 2, "tract"),
    ("contract", "written legal agreement", "/ˈkɒntrækt/", 2, "tract"),
    ("extract", "remove or take out", "/ˈekstrækt/", 2, "tract"),
    ("convention", "large meeting", "/kənˈvenʃn/", 2, "ven"),
    ("intervene", "come between so as to prevent", "/ˌɪntərˈviːn/", 3, "ven"),
    ("revenue", "income of organization", "/ˈrevənjuː/", 3, "ven"),
    ("adventure", "unusual and exciting experience", "/ədˈventʃər/", 2, "ven"),
    ("visible", "able to be seen", "/ˈvɪzəbl/", 1, "vis"),
    ("vision", "ability to see", "/ˈvɪʒn/", 1, "vis"),
    ("visual", "relating to seeing", "/ˈvɪʒuəl/", 2, "vis"),
    ("television", "system for transmitting images", "/ˈtelɪvɪʒn/", 2, "vis"),
    ("vocal", "relating to voice", "/ˈvoʊkl/", 2, "voc"),
    ("vocabulary", "body of words used in language", "/vəˈkæbjələri/", 2, "voc"),
    ("advocate", "publicly recommend", "/ˈædvəkeɪt/", 3, "voc"),
    ("equivocal", "open to more than one interpretation", "/ɪˈkwɪvəkl/", 4, "voc"),
    ("activity", "condition of being active", "/ækˈtɪvəti/", 2, "act"),
    ("activate", "make active", "/ˈæktɪveɪt/", 2, "act"),
    ("audible", "able to be heard", "/ˈɔːdəbl/", 2, "aud"),
    ("microbe", "microscopic organism", "/ˈmaɪkroʊb/", 3, "bio"),
    ("captain", "person in command", "/ˈkæptɪn/", 2, "cap"),
    ("central", "of the center", "/ˈsentrəl/", 2, "cent"),
    ("incredulous", "unwilling to believe", "/ɪnˈkredjələs/", 4, "cred"),
    ("benediction", "utterance of blessing", "/ˌbenɪˈdɪkʃn/", 4, "dict"),
    ("educate", "give intellectual instruction", "/ˈedʒukeɪt/", 2, "duc"),
    ("efficient", "achieving maximum productivity", "/ɪˈfɪʃnt/", 3, "fac"),
    ("inform", "give facts or information", "/ɪnˈfɔːrm/", 2, "form"),
    ("photography", "art of taking photographs", "/fəˈtɒɡrəfi/", 2, "graph"),
    ("eject", "force out suddenly", "/ɪˈdʒekt/", 3, "ject"),
    ("monologue", "long speech by one person", "/ˈmɒnəlɒɡ/", 3, "log"),
    ("maneuver", "movement requiring care", "/məˈnuːvər/", 3, "man"),
    ("promote", "support actively", "/prəˈmoʊt/", 2, "mov"),
    ("impede", "delay or prevent", "/ɪmˈpiːd/", 3, "ped"),
    ("portfolio", "range of investments", "/pɔːrtˈfoʊlioʊ/", 3, "port"),
    ("inscribe", "write or carve on surface", "/ɪnˈskraɪb/", 3, "scrib"),
    ("spectacle", "visually striking performance", "/ˈspektəkl/", 3, "spect"),
    ("obstruct", "block or close", "/əbˈstrʌkt/", 3, "struct"),
    ("protract", "prolong or extend", "/proʊˈtrækt/", 4, "tract"),
    ("prevent", "keep from happening", "/prɪˈvent/", 2, "ven"),
    ("supervise", "observe and direct work", "/ˈsuːpərvaɪz/", 3, "vis"),
    ("provoke", "stimulate strong reaction", "/prəˈvoʊk/", 3, "voc"),
]

SEMANTIC_PAIRS = [
    ("action", "active", 0.82),
    ("action", "react", 0.75),
    ("biology", "biography", 0.70),
    ("biology", "biosphere", 0.78),
    ("capture", "capacity", 0.65),
    ("credit", "credible", 0.80),
    ("dictionary", "predict", 0.68),
    ("factory", "manufacture", 0.85),
    ("form", "format", 0.88),
    ("form", "transform", 0.76),
    ("graph", "graphic", 0.84),
    ("graph", "photograph", 0.72),
    ("project", "reject", 0.55),
    ("logic", "dialogue", 0.62),
    ("manage", "manual", 0.58),
    ("move", "movement", 0.90),
    ("move", "mobile", 0.77),
    ("port", "portable", 0.81),
    ("port", "transport", 0.79),
    ("describe", "script", 0.74),
    ("spectator", "inspect", 0.60),
    ("respect", "perspective", 0.55),
    ("structure", "construct", 0.83),
    ("tractor", "attract", 0.58),
    ("visible", "vision", 0.86),
    ("visible", "visual", 0.88),
    ("vocal", "vocabulary", 0.72),
    ("audience", "audio", 0.75),
    ("conduct", "produce", 0.52),
    ("transmit", "submit", 0.54),
    ("activity", "activate", 0.87),
    ("educate", "conduct", 0.48),
    ("vision", "television", 0.70),
    ("prevent", "intervene", 0.58),
    ("export", "transport", 0.65),
    ("mission", "transmit", 0.50),
]


def seed():
    init_db()
    db = SessionLocal()

    if db.query(Root).count() > 0:
        print("Database already seeded. Skipping.")
        db.close()
        return

    root_map = {}
    for root, meaning, origin, diff in ROOTS:
        r = Root(root=root, meaning=meaning, origin=origin, difficulty=diff)
        db.add(r)
        db.flush()
        root_map[root] = r.id

    word_map = {}
    for word, meaning, phonetic, diff, root_key in VOCABULARY:
        emb = generate_embedding(word, meaning)
        v = Vocabulary(
            word=word,
            meaning=meaning,
            phonetic=phonetic,
            difficulty=diff,
            root_id=root_map.get(root_key),
            embedding_json=dumps(emb),
            example_json=dumps([
                f"Example: The word '{word}' is commonly used in academic writing.",
                f"Students should learn '{word}' through its root {root_key}.",
            ]),
        )
        db.add(v)
        db.flush()
        word_map[word] = v.id
        if root_key in root_map:
            db.add(RootWord(root_id=root_map[root_key], word_id=v.id, relation_type="derived"))

    for w1, w2, score in SEMANTIC_PAIRS:
        if w1 in word_map and w2 in word_map:
            db.add(WordSemanticLink(
                word_id1=word_map[w1],
                word_id2=word_map[w2],
                similarity_score=score,
            ))

    demo = User(
        username="demo",
        password_hash=get_password_hash("demo123"),
        level="intermediate",
        learning_goal="academic",
        cognitive_style="visual",
        profile_json=dumps({"vocab_level": 3, "preferred_scene": "focus"}),
    )
    db.add(demo)
    db.flush()

    sample_words = list(word_map.values())[:15]
    for i, wid in enumerate(sample_words):
        db.add(UserKnowledge(
            user_id=demo.id,
            word_id=wid,
            mastery_level=0.2 + i * 0.04,
            morph_ability=0.3 + i * 0.02,
            semantic_density=0.25 + i * 0.03,
            review_count=i,
        ))

    db.commit()
    print(f"Seeded {len(ROOTS)} roots, {len(VOCABULARY)} words, {len(SEMANTIC_PAIRS)} semantic links")
    print("Demo user: demo / demo123")
    db.close()


if __name__ == "__main__":
    seed()
