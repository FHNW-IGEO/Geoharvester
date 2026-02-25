import { useEffect, useState, useMemo } from "react";
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

function getRotationDegree() {
  const rand = Math.random();
  const degree = rand > 0.5 ? 60 : -60;
  return rand * degree;
}

const fixedValueGenerator = () => 0.5;

type SpiralType = "archimedean" | "rectangular";

export const WordCloud = ({
  open,
  active,
}: {
  open: boolean;
  active: boolean;
}) => {
  const [spiralType, setSpiralType] = useState<SpiralType>("archimedean");
  const [withRotation, setWithRotation] = useState(false);
  const [keywordHistogram, setKeyWordHistogram] = useState<WordData[]>([]);
  const showControls = true;

  useEffect(() => {
    const makeRequest = async () => {
      try {
        const res = await getKeywordHistogram("keywords_nlp_as_tags");
        setKeyWordHistogram(res.data);
      } catch (err) {
        console.error("Error:", err);
      }
    };
    makeRequest();
  }, [open, active]);

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
