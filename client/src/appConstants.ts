
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
    WMTS = "wmts"
}

export enum RESPONSESTATE {
    UNINITIALIZED = "UNINITIALIZED",
    WAITING = "WAITING",
    SUCCESS = "SUCCESS",
    EMPTY = "EMPTY",
    ERROR = "ERROR",
}

