/**
 * Interfaces are based on the schema definition in server/app/redis/schemas
 * As the data is transmitted via JSON string, all field types are now strings.
 *
 */

import { PROVIDER, SERVICE } from "./appConstants";

export interface Geoservice {
  provider: PROVIDER;
  title: string;
  name: string;
  preview: string;
  tree: string;
  group: string;
  abstract: string;
  keywords: string[];
  keywords_nlp: string[];
  legend: string;
  contact: string;
  endpoint: string;
  metadata: string;
  UPDATE: string;
  service: SERVICE;
  max_zoom: number;
  center_lat: string;
  center_lon: string;
  bbox: string;
  metaquality: number;
}

export interface Geodata {
  provider: PROVIDER;
  title: string;
  name: string;
  preview: string;
  abstract: string;
  keywords: string;
  contact: string;
  WMSGetCap: string;
  WMTSGetCap: string;
  WFSGetCap: string;
}

export type SearchParameters = {
  searchString: string | undefined;
  service: SERVICE;
  provider: PROVIDER;
  page: number;
};
