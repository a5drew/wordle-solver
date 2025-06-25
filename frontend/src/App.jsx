import React, { useState, useEffect, useCallback, useRef, memo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, RefreshCw, Sun, Loader2, ServerCrash, HelpCircle, Lightbulb, MousePointerClick, Type, Palette } from 'lucide-react';

// --- API Configuration ---
// Updated to fix the compilation error. In a real build process, this would use environment variables.
const API_URL = 'http://localhost:8000';

// --- COMPONENT: Background ---
const StaticGradientBackground = () => (
    <div className="absolute inset-0 z-0 overflow-hidden bg-slate-950">
        <div className="static-glow-bg"></div>
    </div>
);

// --- COMPONENT: HelpModal (Responsive) ---
const HelpModal = memo(({ onClose }) => {
    const modalVariants = {
        hidden: { opacity: 0, scale: 0.9, y: 50 },
        visible: { opacity: 1, scale: 1, y: 0, transition: { type: 'spring', damping: 15, stiffness: 200 } },
        exit: { opacity: 0, scale: 0.9, y: 50, transition: { duration: 0.2 } },
    };

    const instructionSteps = [
        { icon: Type, text: "Type a 5-letter word or select one from the suggestions list." },
        { icon: Palette, text: "Click on the letters in the current row to set their colors: Grey -> Green -> Yellow." },
        { icon: MousePointerClick, text: "Press Enter or click 'Find Best Words' to submit your feedback." },
        { icon: Lightbulb, text: "The solver will provide a new list of the best possible words to guess next." },
    ];

    return (
        <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
        >
            <motion.div
                className="relative w-full max-w-sm md:max-w-lg bg-slate-800/80 border border-slate-700 rounded-2xl p-6 md:p-8 shadow-2xl"
                variants={modalVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside the modal
            >
                <button onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors">
                    <XCircle size={28} />
                </button>
                <div className="flex items-center gap-3 md:gap-4 mb-6">
                    <HelpCircle className="w-8 h-8 md:w-10 md:h-10 text-cyan-300 flex-shrink-0" />
                    <h2 className="text-2xl md:text-3xl font-bold text-white">How to Use the Solver</h2>
                </div>
                <ul className="space-y-4">
                    {instructionSteps.map((step, index) => (
                        <li key={index} className="flex items-start gap-4">
                            <step.icon className="w-7 h-7 md:w-8 md:h-8 text-cyan-400 mt-1 flex-shrink-0" />
                            <p className="text-base md:text-lg text-slate-300">{step.text}</p>
                        </li>
                    ))}
                </ul>
            </motion.div>
        </motion.div>
    );
});


// --- COMPONENT: Tile ---
const Tile = memo(({ tile, onClick, rowIndex, colIndex, currentRow }) => {
    const isSubmitted = rowIndex < currentRow;
    const tileVariants = {
        hidden: { opacity: 0, scale: 0.8 },
        visible: (custom) => ({ opacity: 1, scale: 1, transition: { delay: custom * 0.04, duration: 0.3, ease: "easeOut" } }),
    };
    const flipVariants = {
        initial: { rotateX: 0 },
        flip: (custom) => ({ rotateX: 360, transition: { delay: custom * 0.1, duration: 0.7, ease: "easeInOut" } })
    };

    return (
        <motion.div layout className="relative w-full h-full" custom={colIndex} initial="hidden" animate="visible" variants={tileVariants}>
            <motion.div onClick={onClick} className="w-full h-full cursor-pointer tile-flipper" style={{ perspective: '1000px' }} variants={flipVariants} animate={isSubmitted ? "flip" : "initial"} custom={colIndex}>
                <motion.div className={`tile-inner w-full h-full rounded-lg flex items-center justify-center text-3xl md:text-4xl font-bold uppercase transition-all duration-300 ${tile.color === 'empty' && 'bg-slate-800/60 border-2 border-slate-700/70'} ${tile.color === 'grey' && 'bg-slate-600 border-slate-600 text-white'} ${tile.color === 'yellow' && 'bg-yellow-500/80 border-yellow-500 text-white shadow-[0_0_20px_rgba(234,179,8,0.5)]'} ${tile.color === 'green' && 'bg-emerald-500/80 border-emerald-500 text-white shadow-[0_0_20px_rgba(16,185,129,0.5)]'}`} style={{ transformStyle: 'preserve-3d' }} whileHover={{ scale: isSubmitted ? 1.05 : 1.0, y: isSubmitted ? -2 : 0, transition: { duration: 0.1 } }} whileTap={{ scale: isSubmitted ? 1.0 : 1.0 }}>
                    <AnimatePresence mode="popLayout"><motion.span key={tile.char} initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.5 }} transition={{ duration: 0.2 }}>{tile.char}</motion.span></AnimatePresence>
                </motion.div>
            </motion.div>
        </motion.div>
    );
});

// --- COMPONENT: GameBoard (Responsive) ---
const GameBoard = ({ grid, onTileClick, currentRow }) => (
    <div className="grid grid-rows-6 grid-cols-5 gap-1.5 md:gap-2 w-full max-w-[340px] md:max-w-sm aspect-[5/6] mb-4 md:mb-8">
        {grid.map((row, rowIndex) => row.map((tile, colIndex) => <Tile key={`${rowIndex}-${colIndex}`} tile={tile} rowIndex={rowIndex} colIndex={colIndex} currentRow={currentRow} onClick={() => onTileClick(rowIndex, colIndex)} />))}
    </div>
);

// --- COMPONENT: Keyboard (Responsive) ---
const Keyboard = memo(({ onKeyClick, keyColors }) => {
    const keyboardLayout = [['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'], ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'], ['ENTER', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', 'BACKSPACE']];
    const getKeyColor = (key) => ({ green: 'bg-emerald-500/80 text-white shadow-[0_0_10px_rgba(16,185,129,0.5)]', yellow: 'bg-yellow-500/80 text-white shadow-[0_0_10px_rgba(234,179,8,0.5)]', grey: 'bg-slate-600 text-white/80' }[keyColors[key]] || 'bg-slate-700/50 hover:bg-slate-600/80');

    return (
        <div className="w-full md:max-w-xl mx-auto px-1 md:px-0">
            {keyboardLayout.map((row, rIndex) => 
                <div key={rIndex} className="flex justify-center gap-1 md:gap-1.5 my-1 md:my-1.5">
                    {row.map(char => {
                        const isSpecialKey = char.length > 1;
                        return (
                            <motion.button 
                                key={char} 
                                data-key={char} 
                                onClick={() => onKeyClick(char)} 
                                // Base classes are mobile, md: prefixes apply for larger screens
                                className={`key h-14 rounded-md font-semibold transition-colors duration-200 flex items-center justify-center ${isSpecialKey ? 'flex-grow-[1.5] text-xs px-1' : 'flex-grow text-sm'} ${getKeyColor(char)}`}
                                whileHover={{ scale: 1.05, y: -2 }} 
                                whileTap={{ scale: 0.95, y: 0 }}
                            >
                                {char === 'BACKSPACE' ? '⌫' : char}
                            </motion.button>
                        );
                    })}
                </div>
            )}
        </div>
    );
});


// --- COMPONENT: AnimatedList ---
const AnimatedList = memo(({ items, onItemSelect, isLoading, error }) => {
    const [selectedIndex, setSelectedIndex] = useState(0);
    const listRef = useRef(null);

    useEffect(() => setSelectedIndex(0), [items]);

    useEffect(() => {
        const handleKeyDown = (e) => {
            if (e.target.closest('.scroll-list-container')) {
                if (e.key === 'ArrowDown') { e.preventDefault(); setSelectedIndex(p => Math.min(p + 1, items.length - 1)); }
                else if (e.key === 'ArrowUp') { e.preventDefault(); setSelectedIndex(p => Math.max(p - 1, 0)); }
                else if (e.key === 'Enter' && selectedIndex >= 0 && selectedIndex < items.length) { e.preventDefault(); onItemSelect(items[selectedIndex]); }
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [items, selectedIndex, onItemSelect]);

    useEffect(() => {
        if (selectedIndex < 0 || !listRef.current) return;
        const selectedItem = listRef.current.querySelector(`[data-index="${selectedIndex}"]`);
        if (selectedItem) selectedItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, [selectedIndex]);

    if (isLoading) return <div className="h-full flex flex-col items-center justify-center text-slate-400"><Loader2 className="w-12 h-12 mb-4 text-cyan-400 animate-spin" /><p>Calculating...</p></div>;
    if (error) return <div className="h-full flex flex-col items-center justify-center text-slate-400 text-center p-4"><ServerCrash className="w-12 h-12 mb-4 text-red-500/70" /><p className="font-semibold text-lg">API Error</p><p className="text-sm">{error}</p></div>;
    if (items.length === 0 && !isLoading) return <div className="h-full flex flex-col items-center justify-center text-slate-400 text-center p-4"><XCircle className="w-12 h-12 mb-4 text-red-500/70" /><p className="font-semibold text-lg">No Words Match</p><p className="text-sm">Adjust colors or reset the board.</p></div>;
    
    return (
        <div className="scroll-list-container relative h-full" tabIndex={-1}>
            <ul ref={listRef} className="scroll-list h-full overflow-y-auto space-y-3 pr-2">
                <AnimatePresence>
                    {items.map((item, index) => {
                        const isSelected = selectedIndex === index;
                        return (
                            <motion.li key={item} data-index={index} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} transition={{ duration: 0.3, delay: index * 0.05 }} onMouseEnter={() => setSelectedIndex(index)} onClick={() => onItemSelect(item)} className={`item ${isSelected ? 'selected' : ''}`}>
                                {isSelected && <motion.div className="selection-glow" layoutId="selection-glow" transition={{ duration: 0.3, ease: "easeOut" }} />}
                                <span className="item-text">{item}</span><span className="item-rank">#{index + 1}</span>
                            </motion.li>
                        );
                    })}
                </AnimatePresence>
            </ul>
        </div>
    );
});

// --- COMPONENT: SuggestionsPanel (Responsive) ---
const SuggestionsPanel = memo(({ suggestions, onSuggestionSelect, onReset, onGenerateNew, isLoading, error }) => (
    <div className="w-full md:w-72 lg:w-80 flex-shrink-0 bg-slate-900/40 p-4 md:p-6 rounded-2xl border border-slate-700/50 flex flex-col backdrop-blur-sm h-[50vh] md:h-[600px]">
        <h2 className="text-2xl md:text-3xl font-bold text-cyan-300 mb-4 tracking-wider flex-shrink-0 flex items-center gap-3">
            <motion.div animate={{ rotate: [0, 10, -5, 0], y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}><Sun size={28} className="text-yellow-300" /></motion.div>
            Suggestions
        </h2>
        <div className="flex-grow overflow-hidden mb-4 rounded-lg bg-slate-900/40 p-2 border border-slate-700/60">
            <AnimatedList items={suggestions} onItemSelect={onSuggestionSelect} isLoading={isLoading} error={error} />
        </div>
        <div className="flex-shrink-0 space-y-3">
            <motion.button disabled={isLoading} onClick={onGenerateNew} whileHover={{ scale: 1.03, y: -2, boxShadow: '0 0 20px rgba(6, 182, 212, 0.5)' }} whileTap={{ scale: 0.97, y: 0 }} className="action-button w-full bg-cyan-600/80 hover:bg-cyan-500/90 text-white font-bold py-3 px-4 rounded-lg transition-all duration-300 tracking-wider uppercase flex items-center justify-center gap-2 border border-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed">
                {isLoading ? <Loader2 size={20} className="animate-spin" /> : <CheckCircle size={20} />} Find Best Words
            </motion.button>
            <motion.button onClick={onReset} whileHover={{ scale: 1.03, y: -2, boxShadow: '0 0 20px rgba(239, 68, 68, 0.5)' }} whileTap={{ scale: 0.97, y: 0 }} className="action-button w-full bg-red-600/80 hover:bg-red-500/90 text-white font-bold py-3 px-4 rounded-lg transition-all duration-300 tracking-wider uppercase flex items-center justify-center gap-2 border border-red-500">
                <RefreshCw size={20} /> Reset
            </motion.button>
        </div>
    </div>
));

// --- Main App Component ---
export default function App() {
    // --- STATE MANAGEMENT ---
    const initialGrid = () => Array.from({ length: 6 }, () => 
        Array.from({ length: 5 }, () => ({ char: '', color: 'empty' }))
    );

    const [grid, setGrid] = useState(initialGrid);
    const [currentRow, setCurrentRow] = useState(0);
    const [currentCol, setCurrentCol] = useState(0);
    const [suggestions, setSuggestions] = useState([]);
    const [keyColors, setKeyColors] = useState({});
    const [isFlipping, setIsFlipping] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isHelpModalOpen, setIsHelpModalOpen] = useState(false); // New state for modal

    // --- API & LOGIC ---
    const handleGenerateNew = useCallback(async (targetRow) => {
        setIsLoading(true);
        setError(null);
        
        const history = grid.slice(0, targetRow).map(row => ({
            guess: row.map(tile => tile.char).join(''),
            feedback: row.map(tile => {
                if (tile.color === 'green') return 'g';
                if (tile.color === 'yellow') return 'y';
                return 'b';
            }).join(''),
        })).filter(item => item.guess.length === 5);

        try {
            const response = await fetch(`${API_URL}/api/suggestions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ history }),
            });
            if (!response.ok) {
                const errorData = await response.text();
                throw new Error(`API Error: ${response.status} - ${errorData}`);
            }
            const data = await response.json();
            setSuggestions(data.suggestions);
        } catch (err) {
            console.error(err);
            setError("Could not connect to solver API. Is it running?");
        } finally {
            setIsLoading(false);
        }
    }, [grid]);

    useEffect(() => {
        handleGenerateNew(0);
    }, []);

    const handleSuggestionSelect = useCallback((word) => {
        if (currentRow >= 6 || isFlipping) return;
        setGrid(g => {
            const newGrid = g.map(row => row.map(tile => ({...tile})));
            newGrid[currentRow] = word.toUpperCase().split('').map(char => ({ char, color: 'empty' }));
            return newGrid;
        });
        setCurrentCol(5);
    }, [currentRow, isFlipping]);

    const handleKeyInput = useCallback((key) => {
        if (currentRow >= 6 || isFlipping) return;

        if (key === 'ENTER') {
            if (currentCol === 5) {
                setIsFlipping(true);
                const newKeyColors = { ...keyColors };
                grid[currentRow].forEach(tile => {
                    const { char, color } = tile;
                    if (!char) return;
                    const charUpper = char.toUpperCase();
                    const existingColor = newKeyColors[charUpper];
                    const effectiveColor = color === 'empty' ? 'grey' : color;
                    if (effectiveColor === 'green' || (effectiveColor === 'yellow' && existingColor !== 'green') || (effectiveColor === 'grey' && !existingColor)) {
                        newKeyColors[charUpper] = effectiveColor;
                    }
                });
                setKeyColors(newKeyColors);
                
                const nextRow = currentRow + 1;
                setCurrentRow(nextRow);
                setCurrentCol(0);
                
                setTimeout(() => {
                    setIsFlipping(false);
                    if(nextRow < 6){
                        handleGenerateNew(nextRow);
                    }
                }, 800);
            }
        } else if (key === 'BACKSPACE') {
            if (currentCol > 0) {
                const newCol = currentCol - 1;
                setGrid(g => {
                    const ng = g.map(r => r.map(t => ({...t})));
                    ng[currentRow][newCol] = { char: '', color: 'empty' };
                    return ng;
                });
                setCurrentCol(newCol);
            }
        } else if (/^[A-Z]$/.test(key) && currentCol < 5) {
            setGrid(g => {
                const ng = g.map(r => r.map(t => ({...t})));
                ng[currentRow][currentCol] = { char: key, color: 'empty' };
                return ng;
            });
            setCurrentCol(prev => prev + 1);
        }
    }, [currentCol, currentRow, isFlipping, grid, keyColors, handleGenerateNew]);
    
    const handleTileClick = (rowIndex, colIndex) => {
        if (rowIndex !== currentRow || !grid[rowIndex][colIndex].char) return;
        const colors = ['empty', 'green', 'yellow'];
        
        setGrid(currentGrid => {
            const newGrid = currentGrid.map(row => row.map(tile => ({ ...tile })));
            const tile = newGrid[rowIndex][colIndex];
            const currentColorIndex = colors.indexOf(tile.color);
            const nextColor = colors[(currentColorIndex + 1) % colors.length];
            
            newGrid[rowIndex][colIndex].color = nextColor;
            return newGrid;
        });
    };

    const handleReset = () => {
        setGrid(initialGrid());
        setCurrentRow(0);
        setCurrentCol(0);
        setKeyColors({});
        setIsFlipping(false);
        setError(null);
        handleGenerateNew(0);
    };

    useEffect(() => {
        const handlePhysicalKeydown = (e) => {
            if (isHelpModalOpen) {
                if (e.key === 'Escape') setIsHelpModalOpen(false);
                return;
            }
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.closest('.scroll-list-container')) return;
            handleKeyInput(e.key.toUpperCase());
        };
        window.addEventListener('keydown', handlePhysicalKeydown);
        return () => window.removeEventListener('keydown', handlePhysicalKeydown);
    }, [handleKeyInput, isHelpModalOpen]);

    return (
        <div className="bg-slate-950 text-gray-100 min-h-screen font-sans flex flex-col items-center justify-start md:justify-center p-4 relative overflow-hidden">
            <StaticGradientBackground />
            <div className="absolute inset-0 z-0 bg-grid-pattern opacity-20"></div>

            <AnimatePresence>
                {isHelpModalOpen && <HelpModal onClose={() => setIsHelpModalOpen(false)} />}
            </AnimatePresence>

            <div className="relative z-10 w-full max-w-6xl mx-auto">
                <header className="text-center my-6 md:mb-10">
                    <div className="flex justify-center items-center gap-x-2 md:gap-x-4">
                        <motion.h1 initial={{ opacity: 0, y: -50 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, ease: "easeOut" }} className="text-4xl md:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-blue-500 tracking-widest uppercase" style={{ textShadow: '0 0 20px rgba(6, 182, 212, 0.5), 0 0 40px rgba(59, 130, 246, 0.4)' }}>
                            Wordle Solver
                        </motion.h1>
                        <motion.button 
                            onClick={() => setIsHelpModalOpen(true)}
                            className="text-slate-500 hover:text-cyan-300 transition-colors shrink-0"
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                            aria-label="How to use"
                        >
                            <HelpCircle size={28} />
                        </motion.button>
                    </div>
                    <motion.p initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.3 }} className="text-slate-400 mt-3 text-base md:text-lg">
                        Enter a word, set the colors, and discover the solution.
                    </motion.p>
                </header>
                <main className="flex flex-col md:flex-row gap-8 md:gap-12 items-center md:items-start justify-center">
                    <div className="w-full flex-grow flex flex-col items-center">
                        <GameBoard grid={grid} onTileClick={handleTileClick} currentRow={currentRow} />
                        <Keyboard onKeyClick={handleKeyInput} keyColors={keyColors} />
                    </div>
                    <SuggestionsPanel
                        suggestions={suggestions}
                        onSuggestionSelect={handleSuggestionSelect}
                        onReset={handleReset}
                        onGenerateNew={() => handleGenerateNew(currentRow)}
                        isLoading={isLoading}
                        error={error}
                    />
                </main>
            </div>
        </div>
    );
}
