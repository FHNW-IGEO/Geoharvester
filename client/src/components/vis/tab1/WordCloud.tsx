import React, { useEffect, useState } from "react";
import { Text } from "@visx/text";
import { scaleLog } from "@visx/scale";
import { Wordcloud } from "@visx/wordcloud";
import { useParentSize, ParentSize } from "@visx/responsive";
import { Box } from "@mui/system";
import { getKeywordHistogram } from "../../../requests";

export interface WordData {
  text: string;
  value: number;
}

const colors = ["#143059", "#2F6B9A", "#82a6c2"];

function wordFreq(text: string): WordData[] {
  const words: string[] = text.replace(/\./g, "").split(/\s/);
  const freqMap: Record<string, number> = {};

  for (const w of words) {
    if (!freqMap[w]) freqMap[w] = 0;
    freqMap[w] += 1;
  }
  return Object.keys(freqMap).map((word) => ({
    text: word,
    value: freqMap[word],
  }));
}

function getRotationDegree() {
  const rand = Math.random();
  const degree = rand > 0.5 ? 60 : -60;
  return rand * degree;
}

const words = wordFreq("aabb cc www");

const fontScale = scaleLog({
  domain: [
    Math.min(...words.map((w) => w.value)),
    Math.max(...words.map((w) => w.value)),
  ],
  range: [10, 100],
});
const fontSizeSetter = (datum: WordData) => fontScale(datum.value);

const fixedValueGenerator = () => 0.5;

type SpiralType = "archimedean" | "rectangular";

export const WordCloud = () => {
  const [spiralType, setSpiralType] = useState<SpiralType>("archimedean");
  const [withRotation, setWithRotation] = useState(false);
  const [keywordHistogram, setKeyWordHistogram] = useState();
  const showControls = true;
  console.log(keywordHistogram);

  useEffect(() => {
    getKeywordHistogram("keywords_nlp").then((res) =>
      setKeyWordHistogram(res.data),
    );
  }, []);

  return (
    <Box sx={{ width: "100%" }}>
      <ParentSize>
        {({ width }) => (
          <Wordcloud
            words={words}
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
                >
                  {w.text}
                </Text>
              ))
            }
          </Wordcloud>
        )}
      </ParentSize>
      {showControls && (
        <div>
          <label>
            Spiral type &nbsp;
            <select
              onChange={(e) => setSpiralType(e.target.value as SpiralType)}
              value={spiralType}
            >
              <option key={"archimedean"} value={"archimedean"}>
                archimedean
              </option>
              <option key={"rectangular"} value={"rectangular"}>
                rectangular
              </option>
            </select>
          </label>
          <label>
            With rotation &nbsp;
            <input
              type="checkbox"
              checked={withRotation}
              onChange={() => setWithRotation(!withRotation)}
            />
          </label>
          <br />
        </div>
      )}
    </Box>
  );
};
