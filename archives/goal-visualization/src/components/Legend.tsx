import React from 'react';

const Legend: React.FC = () => {
    return (
        <div className="legend">
            <div className="legend-column">
                <span className="legend-label">player movement</span>
                <div className="legend-item">
                    <span>with ball</span>
                    <div className="line-sample with-ball" />
                </div>
                <div className="legend-item">
                    <span>without ball</span>
                    <div className="line-sample without-ball" />
                </div>
                <div className="legend-item">
                    <span>player receives<br />or releases ball</span>
                    <div className="dot-sample" />
                </div>
            </div>
            <div className="legend-column">
                <span className="legend-label">ball movement</span>
                <div className="legend-item">
                    <div className="line-sample ball-movement" />
                </div>
                <div className="legend-item">
                    <span>pass/shot</span>
                    <span className="marker pass">◆</span>
                </div>
                <div className="legend-item">
                    <span>other touch</span>
                    <span className="marker touch">◆</span>
                </div>
            </div>
        </div>
    );
};

export default Legend;
