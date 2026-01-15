// Goal data for Argentina vs Serbia & Montenegro 2006
// The famous 26-pass goal by Cambiasso

export interface PlayerPosition {
    id: string;
    name: string;
    x: number; // SVG x coordinate (based on 404 width)
    y: number; // SVG y coordinate (based on 678 height)
}

export interface Pass {
    from: string;
    to: string;
}

export interface PlayerMovement {
    playerId: string;
    withBall: boolean; // true = with ball (solid), false = without ball (lighter)
    path: { x: number; y: number }[];
}

// Player positions (SVG coordinates)
export const players: PlayerPosition[] = [
    { id: 'heinze', name: 'Heinze', x: 140, y: 530 },
    { id: 'mascherano', name: 'Mascherano', x: 130, y: 460 },
    { id: 'sorin', name: 'Sorin', x: 60, y: 380 },
    { id: 'rodriguez', name: 'Rodríguez', x: 150, y: 365 },
    { id: 'riquelme', name: 'Riquelme', x: 180, y: 350 },
    { id: 'ayala', name: 'Ayala', x: 310, y: 340 },
    { id: 'cambiasso', name: 'Cambiasso', x: 295, y: 260 },
    { id: 'saviola', name: 'Saviola', x: 50, y: 175 },
    { id: 'crespo', name: 'Crespo', x: 235, y: 105 },
];

// Player movement paths
export const playerMovements: PlayerMovement[] = [
    // Saviola runs with and without ball
    {
        playerId: 'saviola',
        withBall: true,
        path: [
            { x: 50, y: 175 },
            { x: 80, y: 200 },
            { x: 120, y: 220 },
            { x: 140, y: 250 },
        ]
    },
    {
        playerId: 'saviola',
        withBall: false,
        path: [
            { x: 50, y: 175 },
            { x: 30, y: 150 },
            { x: 45, y: 120 },
            { x: 80, y: 100 },
        ]
    },
    // Crespo movement
    {
        playerId: 'crespo',
        withBall: true,
        path: [
            { x: 235, y: 105 },
            { x: 260, y: 130 },
            { x: 280, y: 150 },
            { x: 300, y: 120 },
        ]
    },
    {
        playerId: 'crespo',
        withBall: false,
        path: [
            { x: 235, y: 105 },
            { x: 200, y: 80 },
            { x: 180, y: 60 },
            { x: 220, y: 50 },
            { x: 260, y: 70 },
        ]
    },
    // Cambiasso runs
    {
        playerId: 'cambiasso',
        withBall: true,
        path: [
            { x: 295, y: 260 },
            { x: 320, y: 230 },
            { x: 340, y: 200 },
        ]
    },
    {
        playerId: 'cambiasso',
        withBall: false,
        path: [
            { x: 295, y: 260 },
            { x: 260, y: 280 },
            { x: 230, y: 260 },
            { x: 250, y: 230 },
        ]
    },
    // Riquelme movement
    {
        playerId: 'riquelme',
        withBall: false,
        path: [
            { x: 180, y: 350 },
            { x: 150, y: 320 },
            { x: 130, y: 280 },
            { x: 160, y: 250 },
        ]
    },
    // Sorin runs
    {
        playerId: 'sorin',
        withBall: false,
        path: [
            { x: 60, y: 380 },
            { x: 40, y: 340 },
            { x: 30, y: 290 },
            { x: 50, y: 250 },
        ]
    },
    // Ayala movement
    {
        playerId: 'ayala',
        withBall: false,
        path: [
            { x: 310, y: 340 },
            { x: 330, y: 310 },
            { x: 350, y: 280 },
            { x: 340, y: 250 },
        ]
    },
];

// Pass sequence
export const passes: Pass[] = [
    { from: 'heinze', to: 'mascherano' },
    { from: 'mascherano', to: 'sorin' },
    { from: 'sorin', to: 'rodriguez' },
    { from: 'rodriguez', to: 'riquelme' },
    { from: 'riquelme', to: 'sorin' },
    { from: 'sorin', to: 'saviola' },
    { from: 'saviola', to: 'riquelme' },
    { from: 'riquelme', to: 'cambiasso' },
    { from: 'cambiasso', to: 'crespo' },
    { from: 'crespo', to: 'saviola' },
    { from: 'saviola', to: 'crespo' },
    { from: 'crespo', to: 'cambiasso' },
    { from: 'cambiasso', to: 'ayala' },
    { from: 'ayala', to: 'riquelme' },
    { from: 'riquelme', to: 'rodriguez' },
    { from: 'rodriguez', to: 'saviola' },
    { from: 'saviola', to: 'sorin' },
    { from: 'sorin', to: 'riquelme' },
    { from: 'riquelme', to: 'cambiasso' },
];

// Ball movement path points (curved path)
export const ballPath = [
    { x: 140, y: 530 },
    { x: 100, y: 450 },
    { x: 60, y: 380 },
    { x: 80, y: 300 },
    { x: 50, y: 220 },
    { x: 100, y: 180 },
    { x: 150, y: 200 },
    { x: 200, y: 180 },
    { x: 250, y: 150 },
    { x: 280, y: 180 },
    { x: 250, y: 220 },
    { x: 200, y: 260 },
    { x: 250, y: 280 },
    { x: 295, y: 260 },
];

export const matchInfo = {
    homeTeam: 'ARGENTINA',
    awayTeam: 'SERBIA and MONTENEGRO',
    year: 2006,
    goalInfo: '2-0 goal in 6-0 win',
};
