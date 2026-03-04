import axios from "axios";
import { Geoservice } from "./types";
import { parseQgisTemplate } from "./templateParser/qgisParser";
import {
  parseArcgisWFS,
  parseArcgisWMSorWMTS,
} from "./templateParser/arcgisParser";
import { LANGUAGE, SERVICE, DEFAULTCHUNKSIZE, PROVIDER } from "./appConstants";

const routes = {
  getData: `/api/getData`,
  getDataByKeywords: `/api/getDataByKeywords`,
  getKeywordHistogram: `/api/getKeywordHistogram`,
  getArcgisproWFS: "/templates/arcgispro_wfs_template.lyrx",
  getArcgisproWMS: "/templates/arcgispro_wms_template.lyrx",
  getArcgisproWMTS: "/templates/arcgispro_wmts_template.lyrx",
  getQgisWFS: "/templates/qgis_wfs_template.qlr",
  getQgisWMS: "/templates/qgis_wms_template.qlr",
  getQgisWMTS: "/templates/qgis_wmts_template.qlr",
};

export const getData = async (
  query_string: string,
  servicetype: SERVICE = SERVICE.NONE,
  providertype: PROVIDER = PROVIDER.NONE,
  lang: LANGUAGE = LANGUAGE.DE,
  pageParam: number = 0,
  size: number = DEFAULTCHUNKSIZE,
) => {
  const page = pageParam + 1; // FastAPI Pagination uses 1 as first index
  const offset = 0;
  const service = servicetype === SERVICE.NONE ? "" : servicetype;
  const provider = providertype === PROVIDER.NONE ? "" : providertype;
  const response = await axios(routes.getData, {
    params: { query_string, service, provider, lang, offset, page, size },
  });
  const result = {
    ...response,
    data: { ...response.data, page: response.data.page - 1 },
  }; // Translate back to zero indexed MUI value
  return result;
};

export const getDataByKeyword = async (
  query_string: string,
  lang: LANGUAGE = LANGUAGE.DE,
  pageParam: number = 0,
  size: number = DEFAULTCHUNKSIZE,
) => {
  const page = pageParam + 1; // FastAPI Pagination uses 1 as first index
  const offset = 0;
  const response = await axios(routes.getDataByKeywords, {
    params: { query_string, lang, offset, page, size },
  });
  const result = {
    ...response,
    data: { ...response.data, page: response.data.page - 1 },
  }; // Translate back to zero indexed MUI value
  return result;
};

export const getKeywordHistogram = async (field: string) => {
  const response = await axios(routes.getKeywordHistogram, {
    params: { field },
  });

  return response;
};

const linkBuilder = (blob: any, fileName: string, fileExtension: string) => {
  const url = window.URL.createObjectURL(new Blob([blob]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", `${fileName}.${fileExtension}`);

  // Build link, download, cleanup:
  document.body.appendChild(link);
  link.click();
  link && link.parentNode && link.parentNode.removeChild(link);
};

export const getArcgisproWFS = async (data: Geoservice) => {
  await fetch(routes.getArcgisproWFS)
    .then((response) => parseArcgisWFS(data, response))
    .then((blob) => linkBuilder(blob, data.title || "filename", "lyrx"));
};
export const getArcgisproWMS = async (data: Geoservice) => {
  await fetch(routes.getArcgisproWMS)
    .then((response) => parseArcgisWMSorWMTS(data, response))
    .then((blob) => linkBuilder(blob, data.title || "filename", "lyrx"));
};
export const getArcgisproWMTS = async (data: Geoservice) => {
  await fetch(routes.getArcgisproWMTS)
    .then((response) => parseArcgisWMSorWMTS(data, response))
    .then((blob) => linkBuilder(blob, data.title || "filename", "lyrx"));
};
export const getQgisWFS = async (data: Geoservice) => {
  await fetch(routes.getQgisWFS)
    .then((response) => parseQgisTemplate(data, response))
    .then((blob) => linkBuilder(blob, data.title || "filename", "qlr"));
};
export const getQgisWMS = async (data: Geoservice) => {
  await fetch(routes.getQgisWMS)
    .then((response) => parseQgisTemplate(data, response))
    .then((blob) => linkBuilder(blob, data.title || "filename", "qlr"));
};
export const getQgisWMTS = async (data: Geoservice) => {
  await fetch(routes.getQgisWMTS)
    .then((response) => parseQgisTemplate(data, response))
    .then((blob) => linkBuilder(blob, data.title || "filename", "qlr"));
};
