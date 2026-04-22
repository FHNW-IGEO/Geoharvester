export const DEFAULTCHUNKSIZE = 1000; // Chunk size retrieved with a single call from redis. Needs to match BE variable of same name!
export const DEFAULTROWSPERPAGE = 100; // Items per page
export const BREAKPOINT600 = 600; // Viewport breakpoint for small UI
export const BREAKPOINT1000 = 1000; // Viewport breakpoint for small UI

export enum LANGUAGE {
  EN = "en",
  DE = "de",
  FR = "fr",
  IT = "it",
}
export const DEFAULTLANGUAGE = LANGUAGE.DE;

export enum PROVIDER {
  NONE = "Alle Quellen",
  BUND = "Bund",
  GEODIENSTE = "Geodienste",
  KT_AG = "KT_AG",
  KT_AI = "KT_AI",
  KT_AR = "KT_AR",
  KT_BE = "KT_BE",
  KT_BL = "KT_BL",
  KT_BS = "KT_BS",
  KT_FR = "KT_FR",
  KT_GE = "KT_GE",
  KT_GL = "KT_GL",
  KT_GR = "KT_GR",
  KT_JU = "KT_JU",
  KT_SG = "KT_SG",
  KT_SH = "KT_SH",
  KT_SO = "KT_SO",
  KT_SZ = "KT_SZ",
  KT_TG = "KT_TG",
  KT_TI = "KT_TI",
  KT_VD = "KT_VD",
  KT_UR = "KT_UR",
  KT_ZG = "KT_ZG",
  KT_ZH = "KT_ZH",
  FL_LI = "FL_LI",
  ST_ZH = "ST_ZH",
  ST_BE = "ST_BE",
  ASIT = "ASIT",
  SOSM = "SOSM",
}

export enum SERVICE {
  NONE = "Alle Services",
  WFS = "wfs",
  WMS = "wms",
  WMTS = "wmts",
}

export enum RESPONSESTATE {
  UNINITIALIZED = "UNINITIALIZED",
  WAITING = "WAITING",
  SUCCESS = "SUCCESS",
  EMPTY = "EMPTY",
  ERROR = "ERROR",
}

export enum KEYWORDFIELD {
  KEYWORDS = "keywords_as_tags",
  KEYWORDS_NLP = "keywords_nlp_as_tags",
  KEYWORDS_de = "keywords_de_as_tags",
  KEYWORDS_NLP_de = "keywords_nlp_de_as_tags",
  KEYWORDS_fr = "keywords_fr_as_tags",
  KEYWORDS_NLP_fr = "keywords_nlp_fr_as_tags",
  KEYWORDS_it = "keywords_it_as_tags",
  KEYWORDS_NLP_it = "keywords_nlp_it_as_tags",
  KEYWORDS_en = "keywords_en_as_tags",
  KEYWORDS_NLP_en = "keywords_nlp_en_as_tags",
}

export const LABELS: Record<string, Record<string, string>> = {
  KEYWORDS: {
    de: "Schlüsselwörter, alle Sprachen",
    en: "Keywords, all languages",
    it: "Parole chiave, tutte le lingue",
    fr: "Mots-clés, toutes langues",
  },
  KEYWORDS_NLP: {
    de: "Schlüsselwörter, generiert, alle Sprachen",
    en: "Keywords, generated, all languages",
    it: "Parole chiave, generate, tutte le lingue",
    fr: "Mots-clés, générés, toutes langues",
  },
};

export const LANG_OPTIONS: Record<string, Record<string, string>> = {
  KEYWORDS_de: {
    field: KEYWORDFIELD.KEYWORDS_de,
    name: "Schlüsselwörter, nur Deutsch",
  },
  KEYWORDS_NLP_de: {
    field: KEYWORDFIELD.KEYWORDS_NLP_de,
    name: "Schlüsselwörter, generiert, nur Deutsch",
  },
  KEYWORDS_en: {
    field: KEYWORDFIELD.KEYWORDS_en,
    name: "Keywords, only English",
  },
  KEYWORDS_NLP_en: {
    field: KEYWORDFIELD.KEYWORDS_NLP_en,
    name: "Keywords, generated, only English",
  },
  KEYWORDS_fr: {
    field: KEYWORDFIELD.KEYWORDS_fr,
    name: "Mots-clés, seulement Français",
  },
  KEYWORDS_NLP_fr: {
    field: KEYWORDFIELD.KEYWORDS_NLP_fr,
    name: "Mots-clés, générés, seulement Français",
  },
  KEYWORDS_it: {
    field: KEYWORDFIELD.KEYWORDS_NLP_it,
    name: "Parole chiave, solo Italiano",
  },
  KEYWORDS_NLP_it: {
    field: KEYWORDFIELD.KEYWORDS_NLP_it,
    name: "Parole chiave, generate, solo Italiano",
  },
};
