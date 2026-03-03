import { useEffect, useState, useMemo } from "react";
import { Text } from "@visx/text";
import { scaleLog } from "@visx/scale";
import { Wordcloud } from "@visx/wordcloud";
import { useParentSize, ParentSize } from "@visx/responsive";
import { Box } from "@mui/system";
import { getKeywordHistogram } from "../../../requests";
import {
  AppBar,
  Drawer,
  IconButton,
  Toolbar,
  Typography,
  useTheme,
  Tab,
} from "@mui/material";
import { KEYWORDFIELD, LANGUAGE } from "../../../appConstants";
import { WordCloudToolbar } from "./WordCloudToolbar";

export interface WordData {
  text: string;
  value: number;
}

const colors = ["#143059", "#2F6B9A", "#82a6c2"];

function getRotationDegree() {
  const rand = Math.random();
  const degree = rand > 0.5 ? 60 : -60;
  return rand * degree;
}

const fixedValueGenerator = () => 0.5;

export type SpiralType = "archimedean" | "rectangular";

export const WordCloud = ({
  open,
  active,
  language,
}: {
  open: boolean;
  active: boolean;
  language: LANGUAGE;
}) => {
  const [spiralType, setSpiralType] = useState<SpiralType>("archimedean");
  const [withRotation, setWithRotation] = useState(false);
  const [keywordHistogram, setKeyWordHistogram] = useState<WordData[]>([]);
  const [keywordfieldToSearch, setKeywordfieldToSearch] =
    useState<KEYWORDFIELD>(KEYWORDFIELD.KEYWORDS);
  const theme = useTheme();

  useEffect(() => {
    const makeRequest = async () => {
      try {
        const res = await getKeywordHistogram(keywordfieldToSearch);
        setKeyWordHistogram(res.data);
      } catch (err) {
        console.error("Error:", err);
      }
    };
    makeRequest();
  }, [open, active, keywordfieldToSearch]);

  const fontScale = useMemo(() => {
    if (!keywordHistogram || keywordHistogram.length === 0) return null;

    const values = keywordHistogram.map((w) => w.value);
    return scaleLog({
      domain: [Math.min(...values), Math.max(...values)],
      range: [12, 50],
    });
  }, [keywordHistogram]);

  const fontSizeSetter = (datum: WordData) =>
    fontScale ? fontScale(datum.value) : 0;

  return (
    <>
      <AppBar
        position="static"
        sx={{
          backgroundColor: theme.palette.secondary.main,
          padding: 0,
          height: 50,
          display: "flex",
          justifyContent: "center",
        }}
      >
        <Toolbar>
          <WordCloudToolbar
            {...{
              language,
              keywordfieldToSearch,
              setKeywordfieldToSearch,
              setSpiralType,
              spiralType,
              withRotation,
              setWithRotation,
            }}
          />
        </Toolbar>
      </AppBar>
      <Box sx={{ width: "100%" }}>
        <ParentSize>
          {({ width }) => (
            <Wordcloud
              words={keywordHistogram}
              width={width}
              height={width * 0.5}
              fontSize={fontSizeSetter}
              font={"Impact"}
              padding={2}
              spiral={spiralType}
              rotate={withRotation ? getRotationDegree : 0}
              random={fixedValueGenerator}
            >
              {(cloudWords) =>
                cloudWords.map((w, i) => (
                  <Text
                    key={w.text}
                    fill={colors[i % colors.length]}
                    textAnchor={"middle"}
                    transform={`translate(${w.x}, ${w.y}) rotate(${w.rotate})`}
                    fontSize={w.size}
                    fontFamily={w.font}
                    onClick={() => console.log(w.text)}
                    style={{ cursor: "pointer" }}
                  >
                    {w.text}
                  </Text>
                ))
              }
            </Wordcloud>
          )}
        </ParentSize>
      </Box>
    </>
  );
};
