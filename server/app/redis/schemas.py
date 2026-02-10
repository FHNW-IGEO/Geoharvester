
from typing import List, Optional

from pydantic import BaseModel, field_validator
from redis.commands.search.field import (GeoField, NumericField, TextField,
                                         TextField)
from typing import Optional, List, Union

### Geoservices
# Source data:  https://github.com/davidoesch/geoservice_harvester_poc/tree/main/data/geoservices_CH.csv

SVC_PREFIX = "svc:"    
SVC_KEY = SVC_PREFIX + '{}'
SVC_INDEX_ID = "py_{}_idx".format(SVC_PREFIX)

geoservices_schema = (
    TextField('$.provider', as_name='provider', no_stem=True),
    TextField('$.title', as_name='title'),
    TextField('$.name', as_name='name'),
    TextField('$.preview', as_name='preview'),
    TextField('$.tree', as_name='tree', no_stem=True,),
    TextField('$.group', as_name='group', no_stem=True,),
    TextField('$.abstract', as_name='abstract'),
    TextField('$.keywords', as_name='keywords'),
    TextField('$.keywords_nlp', as_name='keywords_nlp'),
    TextField('$.legend', as_name='legend', no_stem=True,),
    TextField('$.contact', as_name='contact', no_stem=True,),
    TextField('$.endpoint', as_name='endpoint', no_stem=True,),
    TextField('$.metadata', as_name='metadata', no_stem=True,),
    # TextField('$.update', as_name='update', no_stem=True,),# WARNING: field not used
    TextField('$.service', as_name='service'),
    NumericField('$.max_zoom', as_name='max_zoom'),
    NumericField('$.center_lat', as_name='center_lat'),
    NumericField('$.center_lon', as_name='center_lon'),
    TextField('$.bbox', as_name='bbox', no_stem=True,),
    TextField('$.summary', as_name='summary', no_stem=True,),
    TextField('$.lang_3', as_name='lang_3'),
    # TextField('$.lang_2', as_name='lang_2'), # WARNING field not used
    NumericField('$.metaquality', as_name='metaquality'),
    TextField('$.title_en', as_name='title_en'),
    TextField('$.title_de', as_name='title_de'),
    TextField('$.title_it', as_name='title_it'),
    TextField('$.title_fr', as_name='title_fr'),
    TextField('$.abstract_en', as_name='abstract_en'),
    TextField('$.abstract_de', as_name='abstract_de'),
    TextField('$.abstract_it', as_name='abstract_it'),
    TextField('$.abstract_fr', as_name='abstract_fr'),
    TextField('$.keywords_en', as_name='keywords_en'),
    TextField('$.keywords_de', as_name='keywords_de'),
    TextField('$.keywords_it', as_name='keywords_it'),
    TextField('$.keywords_fr', as_name='keywords_fr'),
    TextField('$.keywords_nlp_en', as_name='keywords_nlp_en'),
    TextField('$.keywords_nlp_de', as_name='keywords_nlp_de'),
    TextField('$.keywords_nlp_it', as_name='keywords_nlp_it'),
    TextField('$.keywords_nlp_fr', as_name='keywords_nlp_fr'),
    )


class GeoserviceModel(BaseModel):
    # Add only fields that are returned here
    # Any fields added (optional or not) need to be returned by the search_redis method in redis/methods.py
    _primary_key_field: str = "id"
    provider: str
    title: str
    name: str

    preview: Optional[str] = ""
    tree: Optional[str] = ""
    group: Optional[str] = ""
    abstract: Optional[str] = ""
    legend: Optional[str] = ""
    metadata: Optional[str] = ""
    contact: Optional[str] = ""
    endpoint: Optional[str] = ""
    service: Optional[str] = ""
    max_zoom: Optional[int] = None
    bbox: Optional[str] = ""
    center_lat: Optional[float] = None
    center_lon: Optional[float] = None
    metaquality: Optional[int] = 0

    keywords: Optional[Union[str, List[str]]] = None
    keywords_nlp: Optional[Union[str, List[str]]] = None
    lang_3: Optional[Union[str, List[str]]] = None

    @field_validator("keywords", "keywords_nlp", "lang_3", mode="before")
    @classmethod
    def normalize_to_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            # split only if needed
            return [s.strip() for s in v.split(",")] if "," in v else [v]
        return v

    class Config:
        from_attributes = True
