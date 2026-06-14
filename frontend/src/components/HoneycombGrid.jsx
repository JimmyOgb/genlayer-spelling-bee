import { useState } from "react";

/**
 * HoneycombGrid
 * Renders the classic 7-hex Spelling Bee layout:
 *   one center hex surrounded by six outer hexes.
 *
 * Props:
 *   centerLetter  string   The required center letter
 *   outerLetters  string[] The 6 surrounding letters
 *   onHint        (letter: string) => void   Called when user requests a hint
 */
export default function HoneycombGrid({ centerLetter, outerLetters, onHint }) {
  const [hoveredLetter, setHoveredLetter] = useState(null);

  // Hex geometry (flat-top, in SVG units)
  const HEX_SIZE = 52;
  const HEX_GAP = 6;
  const STEP = HEX_SIZE * 2 - HEX_SIZE * 0.5 + HEX_GAP;

  // Positions for a standard 7-hex flower layout (center + 6 around)
  const positions = [
    { x: 0, y: 0 },                        // center
    { x: STEP * Math.cos(Math.PI / 6) * 1.15, y: -STEP * 0.5 * 1.3 }, // top-right
    { x: STEP * Math.cos(Math.PI / 6) * 1.15, y:  STEP * 0.5 * 1.3 }, // bottom-right
    { x: 0,                                 y: -STEP * 1.3 },           // top
    { x: 0,                                 y:  STEP * 1.3 },           // bottom
    { x: -STEP * Math.cos(Math.PI / 6) * 1.15, y: -STEP * 0.5 * 1.3 },// top-left
    { x: -STEP * Math.cos(Math.PI / 6) * 1.15, y:  STEP * 0.5 * 1.3 },// bottom-left
  ];

  const letters = [centerLetter, ...outerLetters];
  const isCenter = (idx) => idx === 0;

  // SVG hexagon path for flat-top hex
  const hexPath = (size) => {
    const pts = Array.from({ length: 6 }, (_, i) => {
      const angle = (Math.PI / 180) * (60 * i - 30);
      return `${size * Math.cos(angle)},${size * Math.sin(angle)}`;
    });
    return `M ${pts.join(" L ")} Z`;
  };

  const viewBoxSize = 380;
  const cx = viewBoxSize / 2;
  const cy = viewBoxSize / 2;

  return (
    <div className="flex flex-col items-center gap-4">
      <svg
        width={viewBoxSize}
        height={viewBoxSize}
        viewBox={`0 0 ${viewBoxSize} ${viewBoxSize}`}
        className="max-w-[320px] w-full"
      >
        {letters.map((letter, idx) => {
          const { x, y } = positions[idx];
          const cx_ = cx + x;
          const cy_ = cy + y;
          const center = isCenter(idx);
          const hovered = hoveredLetter === idx;

          return (
            <g
              key={idx}
              transform={`translate(${cx_}, ${cy_})`}
              onClick={() => onHint && onHint(letter)}
              onMouseEnter={() => setHoveredLetter(idx)}
              onMouseLeave={() => setHoveredLetter(null)}
              className="cursor-pointer"
            >
              {/* Hex background */}
              <path
                d={hexPath(HEX_SIZE)}
                fill={
                  center
                    ? hovered ? "#f5c518" : "#f5c518cc"
                    : hovered ? "#2a2a35" : "#1e1e28"
                }
                stroke={center ? "#f5c518" : "#3a3a4a"}
                strokeWidth={center ? 2 : 1.5}
                className="transition-colors duration-150"
              />
              {/* Letter */}
              <text
                textAnchor="middle"
                dominantBaseline="central"
                fontSize={center ? 28 : 24}
                fontWeight={center ? "bold" : "600"}
                fill={center ? "#0f0f13" : "#ffffff"}
                className="select-none pointer-events-none font-sans tracking-wider"
                style={{ fontFamily: "system-ui, sans-serif" }}
              >
                {letter}
              </text>
              {/* Hint tooltip hint */}
              {center && (
                <title>Click letter for hint</title>
              )}
            </g>
          );
        })}
      </svg>

      {/* Hint instruction */}
      <p className="text-xs text-white/30 text-center">
        Click any letter for a hint on words starting with it
      </p>
    </div>
  );
}
