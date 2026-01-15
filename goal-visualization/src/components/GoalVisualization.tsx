import React from 'react';
import Pitch from './Pitch';
import { players, passes, ballPath, playerMovements } from '../data/goalData';

const GoalVisualization: React.FC = () => {
    // Get player position by id
    const getPlayer = (id: string) => players.find(p => p.id === id);

    // Generate curved path for ball movement
    const generateBallPath = () => {
        if (ballPath.length < 2) return '';
        let d = `M ${ballPath[0].x} ${ballPath[0].y}`;
        for (let i = 1; i < ballPath.length; i++) {
            const prev = ballPath[i - 1];
            const curr = ballPath[i];
            const cx = (prev.x + curr.x) / 2;
            const cy = (prev.y + curr.y) / 2 - 20;
            d += ` Q ${cx} ${cy}, ${curr.x} ${curr.y}`;
        }
        return d;
    };

    // Generate path string for player movement
    const generateMovementPath = (points: { x: number; y: number }[]) => {
        if (points.length < 2) return '';
        let d = `M ${points[0].x} ${points[0].y}`;
        for (let i = 1; i < points.length; i++) {
            const prev = points[i - 1];
            const curr = points[i];
            const cx = (prev.x + curr.x) / 2;
            const cy = (prev.y + curr.y) / 2;
            d += ` Q ${cx} ${cy}, ${curr.x} ${curr.y}`;
        }
        return d;
    };

    return (
        <div className="goal-visualization">
            <svg viewBox="0 0 404 678" className="visualization-svg">
                {/* Pitch as background - white strokes on blue */}
                <g color="rgba(255,255,255,0.5)">
                    <Pitch />
                </g>

                {/* Player movement paths - WITHOUT ball (lighter, rendered first/bottom) */}
                {playerMovements
                    .filter(m => !m.withBall)
                    .map((movement, i) => (
                        <path
                            key={`movement-no-ball-${i}`}
                            d={generateMovementPath(movement.path)}
                            fill="none"
                            stroke="rgba(37, 99, 235, 0.35)"
                            strokeWidth="8"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        />
                    ))
                }

                {/* Player movement paths - WITH ball (solid) */}
                {playerMovements
                    .filter(m => m.withBall)
                    .map((movement, i) => (
                        <path
                            key={`movement-ball-${i}`}
                            d={generateMovementPath(movement.path)}
                            fill="none"
                            stroke="#2563EB"
                            strokeWidth="8"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        />
                    ))
                }

                {/* Ball movement path - rendered ON TOP of player movements */}
                <path
                    d={generateBallPath()}
                    fill="none"
                    stroke="rgba(130, 200, 240, 0.9)"
                    strokeWidth="6"
                    strokeLinecap="round"
                />

                {/* Pass lines - rendered ON TOP */}
                {passes.map((pass, i) => {
                    const from = getPlayer(pass.from);
                    const to = getPlayer(pass.to);
                    if (!from || !to) return null;
                    return (
                        <line
                            key={i}
                            x1={from.x}
                            y1={from.y}
                            x2={to.x}
                            y2={to.y}
                            stroke="#D4A843"
                            strokeWidth="2"
                        />
                    );
                })}


                {/* Touch points */}
                {passes.map((pass, i) => {
                    const from = getPlayer(pass.from);
                    if (!from) return null;
                    return (
                        <circle
                            key={`touch-${i}`}
                            cx={from.x}
                            cy={from.y}
                            r="3"
                            fill="#D4A843"
                        />
                    );
                })}

                {/* Player markers */}
                {players.map((player) => (
                    <g key={player.id} transform={`translate(${player.x}, ${player.y})`}>
                        {/* Capsule shape - rotated */}
                        <g transform="rotate(-45)">
                            <ellipse cx="0" cy="0" rx="18" ry="6" fill="#2563EB" />
                            <circle cx="-12" cy="0" r="6" fill="#2563EB" />
                            <circle cx="12" cy="0" r="6" fill="#2563EB" />
                        </g>
                        {/* Player name */}
                        <text
                            x="15"
                            y="18"
                            fontSize="12"
                            fill="#1a1a1a"
                            fontFamily="sans-serif"
                            fontWeight="500"
                        >
                            {player.name}
                        </text>
                    </g>
                ))}
            </svg>
        </div>
    );
};

export default GoalVisualization;

