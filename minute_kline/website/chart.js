"use strict";


const STOCK_CODES = [
    "sh600231",
    "sh600438",
    "sh600763",
    "sh601012",
    "sh601500",
    "sh601636",
    "sh603259",
    "sh603799",
    "sz000100",
    "sz002067",
    "sz002129",
    "sz002230",
    "sz002361",
    "sz002600",
    "sz300274",
    "sz300433",
];


const DEFAULT_STOCK_CODE = "sz002067";
const DEFAULT_ADJUST_NAME = "qfq";
const DEFAULT_VISIBLE_BARS = 500;

const UP_COLOR = "#ef4444";
const DOWN_COLOR = "#16a34a";

const UP_VOLUME_COLOR =
    "rgba(239, 68, 68, 0.52)";

const DOWN_VOLUME_COLOR =
    "rgba(22, 163, 74, 0.52)";


const chartContainer =
    document.getElementById("chart");

const stockSelect =
    document.getElementById("stock-select");

const adjustSelect =
    document.getElementById("adjust-select");

const resetViewButton =
    document.getElementById(
        "reset-view-button"
    );

const chartTitle =
    document.getElementById("chart-title");

const connectionBadge =
    document.getElementById(
        "connection-badge"
    );

const loadingMessage =
    document.getElementById(
        "loading-message"
    );

const errorMessage =
    document.getElementById(
        "error-message"
    );

const barCount =
    document.getElementById("bar-count");

const startTime =
    document.getElementById("start-time");

const endTime =
    document.getElementById("end-time");

const ohlcvDisplay =
    document.getElementById(
        "ohlcv-display"
    );


let currentCandlestickData = [];
let activeRequestNumber = 0;


function assertPageElements() {
    const requiredElements = {
        chartContainer,
        stockSelect,
        adjustSelect,
        resetViewButton,
        chartTitle,
        connectionBadge,
        loadingMessage,
        errorMessage,
        barCount,
        startTime,
        endTime,
        ohlcvDisplay,
    };

    for (
        const [name, element]
        of Object.entries(requiredElements)
    ) {
        if (!element) {
            throw new Error(
                `Missing page element: ${name}.`
            );
        }
    }

    if (
        typeof LightweightCharts
        === "undefined"
    ) {
        throw new Error(
            "Lightweight Charts failed to load."
        );
    }
}


assertPageElements();


const chart =
    LightweightCharts.createChart(
        chartContainer,
        {
            width:
                chartContainer.clientWidth,

            height:
                chartContainer.clientHeight,

            layout: {
                background: {
                    type:
                        LightweightCharts
                            .ColorType
                            .Solid,

                    color: "#ffffff",
                },

                textColor: "#475467",

                panes: {
                    separatorColor:
                        "#e4e7ec",

                    separatorHoverColor:
                        "#98a2b3",

                    enableResize: true,
                },
            },

            grid: {
                vertLines: {
                    color: "#f2f4f7",
                },

                horzLines: {
                    color: "#f2f4f7",
                },
            },

            rightPriceScale: {
                borderColor: "#d0d5dd",
            },

            timeScale: {
                borderColor: "#d0d5dd",
                timeVisible: true,
                secondsVisible: false,
                rightOffset: 8,
                barSpacing: 8,
                minBarSpacing: 0.5,
            },

            crosshair: {
                mode:
                    LightweightCharts
                        .CrosshairMode
                        .Normal,
            },

            handleScroll: {
                mouseWheel: true,
                pressedMouseMove: true,
                horzTouchDrag: true,
                vertTouchDrag: false,
            },

            handleScale: {
                axisPressedMouseMove: true,
                mouseWheel: true,
                pinch: true,
            },

            localization: {
                locale: "zh-CN",
            },
        }
    );


const candlestickSeries =
    chart.addSeries(
        LightweightCharts
            .CandlestickSeries,

        {
            upColor: UP_COLOR,
            downColor: DOWN_COLOR,

            borderUpColor: UP_COLOR,
            borderDownColor: DOWN_COLOR,

            wickUpColor: UP_COLOR,
            wickDownColor: DOWN_COLOR,

            priceFormat: {
                type: "price",
                precision: 4,
                minMove: 0.0001,
            },
        },

        0
    );


const volumeSeries =
    chart.addSeries(
        LightweightCharts
            .HistogramSeries,

        {
            priceFormat: {
                type: "volume",
            },

            priceLineVisible: false,
            lastValueVisible: false,
        },

        1
    );


const chartPanes = chart.panes();

if (chartPanes.length > 1) {
    chartPanes[1].setHeight(180);
}


function populateStockSelect() {
    const fragment =
        document.createDocumentFragment();

    for (
        const stockCode
        of STOCK_CODES
    ) {
        const option =
            document.createElement(
                "option"
            );

        option.value = stockCode;

        option.textContent =
            stockCode.toUpperCase();

        fragment.appendChild(option);
    }

    stockSelect.replaceChildren(
        fragment
    );

    stockSelect.value =
        DEFAULT_STOCK_CODE;

    adjustSelect.value =
        DEFAULT_ADJUST_NAME;
}


function getDataFileCandidates(
    stockCode,
    adjustName
) {
    return [
        (
            `./data/${adjustName}/`
            + `${stockCode}_5min_`
            + `${adjustName}.json`
        ),

        (
            `./data/${adjustName}/`
            + `${stockCode}_5min_`
            + `${adjustName}`
            + `_baostock.json`
        ),
    ];
}


async function fetchFirstAvailableJson(
    filePathCandidates
) {
    const failedRequests = [];

    for (
        const filePath
        of filePathCandidates
    ) {
        try {
            const response =
                await fetch(
                    filePath,
                    {
                        cache: "no-store",
                    }
                );

            if (response.ok) {
                return {
                    filePath,

                    data:
                        await response.json(),
                };
            }

            failedRequests.push(
                (
                    `${filePath} `
                    + `(HTTP `
                    + `${response.status})`
                )
            );

        } catch (error) {
            failedRequests.push(
                (
                    `${filePath} `
                    + `(${error.message})`
                )
            );
        }
    }

    throw new Error(
        (
            "Unable to load the "
            + "selected JSON file. "
            + "Tried: "
            + `${failedRequests.join(", ")}.`
        )
    );
}


function normalizeKlineData(
    rawData
) {
    if (
        !Array.isArray(rawData)
        || rawData.length === 0
    ) {
        throw new Error(
            "The selected JSON "
            + "dataset is empty."
        );
    }

    const normalizedRows =
        rawData.map(
            (row, index) => {
                const normalizedRow = {
                    time:
                        Number(row.time),

                    open:
                        Number(row.open),

                    high:
                        Number(row.high),

                    low:
                        Number(row.low),

                    close:
                        Number(row.close),

                    volume:
                        Number(row.volume),
                };

                const values =
                    Object.values(
                        normalizedRow
                    );

                if (
                    !values.every(
                        Number.isFinite
                    )
                ) {
                    throw new Error(
                        (
                            "Invalid numeric "
                            + "data at row "
                            + `${index}.`
                        )
                    );
                }

                const maximumPrice =
                    Math.max(
                        normalizedRow.open,
                        normalizedRow.close,
                        normalizedRow.low
                    );

                const minimumPrice =
                    Math.min(
                        normalizedRow.open,
                        normalizedRow.close,
                        normalizedRow.high
                    );

                if (
                    normalizedRow.high
                        < maximumPrice
                    ||
                    normalizedRow.low
                        > minimumPrice
                ) {
                    throw new Error(
                        (
                            "Invalid OHLC "
                            + "relationship "
                            + `at row ${index}.`
                        )
                    );
                }

                return normalizedRow;
            }
        );

    normalizedRows.sort(
        (
            firstRow,
            secondRow
        ) =>
            firstRow.time
            - secondRow.time
    );

    const uniqueRows = [];
    let previousTime = null;

    for (
        const row
        of normalizedRows
    ) {
        if (
            row.time
            === previousTime
        ) {
            uniqueRows[
                uniqueRows.length - 1
            ] = row;

        } else {
            uniqueRows.push(row);
        }

        previousTime = row.time;
    }

    return uniqueRows;
}


function buildSeriesData(
    normalizedRows
) {
    const candlestickData =
        normalizedRows.map(
            (row) => ({
                time: row.time,
                open: row.open,
                high: row.high,
                low: row.low,
                close: row.close,
            })
        );

    const volumeData =
        normalizedRows.map(
            (row) => ({
                time: row.time,
                value: row.volume,

                color:
                    row.close >= row.open
                        ? UP_VOLUME_COLOR
                        : DOWN_VOLUME_COLOR,
            })
        );

    return {
        candlestickData,
        volumeData,
    };
}


function formatTimestamp(
    timestamp
) {
    const date =
        new Date(timestamp * 1000);

    const year =
        date.getUTCFullYear();

    const month =
        String(
            date.getUTCMonth() + 1
        ).padStart(2, "0");

    const day =
        String(
            date.getUTCDate()
        ).padStart(2, "0");

    const hour =
        String(
            date.getUTCHours()
        ).padStart(2, "0");

    const minute =
        String(
            date.getUTCMinutes()
        ).padStart(2, "0");

    return (
        `${year}-${month}-${day} `
        + `${hour}:${minute}`
    );
}


function formatPrice(value) {
    return Number(value).toFixed(4);
}


function formatVolume(value) {
    return Number(
        value
    ).toLocaleString(
        "en-US",
        {
            maximumFractionDigits: 0,
        }
    );
}


function setLoadingState(message) {
    connectionBadge.textContent =
        "Loading";

    connectionBadge.className =
        "status-badge loading";

    loadingMessage.textContent =
        message;

    loadingMessage.style.display =
        "block";

    errorMessage.textContent = "";

    errorMessage.style.display =
        "none";

    stockSelect.disabled = true;
    adjustSelect.disabled = true;
}


function setSuccessState(message) {
    connectionBadge.textContent =
        "Ready";

    connectionBadge.className =
        "status-badge success";

    loadingMessage.textContent =
        message;

    loadingMessage.style.display =
        "block";

    errorMessage.textContent = "";

    errorMessage.style.display =
        "none";

    stockSelect.disabled = false;
    adjustSelect.disabled = false;
}


function setFailedState(error) {
    connectionBadge.textContent =
        "Failed";

    connectionBadge.className =
        "status-badge failed";

    loadingMessage.textContent = "";

    loadingMessage.style.display =
        "none";

    errorMessage.textContent =
        `[FAILED] ${error.message}`;

    errorMessage.style.display =
        "block";

    stockSelect.disabled = false;
    adjustSelect.disabled = false;
}


function showLatestRange() {
    const totalBars =
        currentCandlestickData.length;

    if (totalBars === 0) {
        return;
    }

    chart
        .timeScale()
        .setVisibleLogicalRange(
            {
                from: Math.max(
                    0,
                    (
                        totalBars
                        - DEFAULT_VISIBLE_BARS
                    )
                ),

                to: totalBars - 1,
            }
        );
}


function updateSummary(
    stockCode,
    adjustName,
    sourceFilePath
) {
    const firstBar =
        currentCandlestickData[0];

    const lastBar =
        currentCandlestickData[
            currentCandlestickData.length
            - 1
        ];

    chartTitle.textContent =
        (
            `${stockCode.toUpperCase()}`
            + " · 5-Minute "
            + `${adjustName.toUpperCase()}`
            + " K-Line"
        );

    barCount.textContent =
        currentCandlestickData
            .length
            .toLocaleString("en-US");

    startTime.textContent =
        formatTimestamp(
            firstBar.time
        );

    endTime.textContent =
        formatTimestamp(
            lastBar.time
        );

    ohlcvDisplay.textContent =
        (
            `O ${formatPrice(lastBar.open)} · `
            + `H ${formatPrice(lastBar.high)} · `
            + `L ${formatPrice(lastBar.low)} · `
            + `C ${formatPrice(lastBar.close)}`
        );

    console.log(
        (
            "[SUCCESS] Loaded "
            + `${currentCandlestickData.length}`
            + " bars from "
            + `${sourceFilePath}.`
        )
    );
}


async function loadSelectedKlineData() {
    const requestNumber =
        ++activeRequestNumber;

    const stockCode =
        stockSelect.value;

    const adjustName =
        adjustSelect.value;

    setLoadingState(
        (
            "Loading "
            + `${stockCode.toUpperCase()} `
            + `${adjustName.toUpperCase()} `
            + "data..."
        )
    );

    try {
        const filePathCandidates =
            getDataFileCandidates(
                stockCode,
                adjustName
            );

        const {
            filePath,
            data: rawData,
        } =
            await fetchFirstAvailableJson(
                filePathCandidates
            );

        if (
            requestNumber
            !== activeRequestNumber
        ) {
            return;
        }

        const normalizedRows =
            normalizeKlineData(
                rawData
            );

        const {
            candlestickData,
            volumeData,
        } =
            buildSeriesData(
                normalizedRows
            );

        currentCandlestickData =
            candlestickData;

        candlestickSeries.setData(
            candlestickData
        );

        volumeSeries.setData(
            volumeData
        );

        showLatestRange();

        updateSummary(
            stockCode,
            adjustName,
            filePath
        );

        setSuccessState(
            (
                "Loaded "
                + `${candlestickData
                    .length
                    .toLocaleString("en-US")}`
                + " bars."
            )
        );

    } catch (error) {
        if (
            requestNumber
            !== activeRequestNumber
        ) {
            return;
        }

        console.error(error);

        currentCandlestickData = [];

        candlestickSeries.setData([]);
        volumeSeries.setData([]);

        barCount.textContent = "—";
        startTime.textContent = "—";
        endTime.textContent = "—";

        ohlcvDisplay.textContent =
            "Unable to display data";

        setFailedState(error);
    }
}


chart.subscribeCrosshairMove(
    (parameter) => {
        const point =
            parameter.point;

        if (
            !parameter.time
            || point === undefined
            || point.x < 0
            || point.y < 0
            || point.x
                > chartContainer.clientWidth
            || point.y
                > chartContainer.clientHeight
        ) {
            if (
                currentCandlestickData
                    .length > 0
            ) {
                const latestBar =
                    currentCandlestickData[
                        currentCandlestickData
                            .length - 1
                    ];

                ohlcvDisplay.textContent =
                    (
                        `O ${formatPrice(
                            latestBar.open
                        )} · `

                        + `H ${formatPrice(
                            latestBar.high
                        )} · `

                        + `L ${formatPrice(
                            latestBar.low
                        )} · `

                        + `C ${formatPrice(
                            latestBar.close
                        )}`
                    );
            }

            return;
        }

        const candle =
            parameter.seriesData.get(
                candlestickSeries
            );

        const volume =
            parameter.seriesData.get(
                volumeSeries
            );

        if (!candle) {
            return;
        }

        const volumeText =
            volume
                ? (
                    ` · V ${formatVolume(
                        volume.value
                    )}`
                )
                : "";

        ohlcvDisplay.textContent =
            (
                `${formatTimestamp(
                    Number(parameter.time)
                )} · `

                + `O ${formatPrice(
                    candle.open
                )} · `

                + `H ${formatPrice(
                    candle.high
                )} · `

                + `L ${formatPrice(
                    candle.low
                )} · `

                + `C ${formatPrice(
                    candle.close
                )}`

                + volumeText
            );
    }
);


stockSelect.addEventListener(
    "change",
    loadSelectedKlineData
);


adjustSelect.addEventListener(
    "change",
    loadSelectedKlineData
);


resetViewButton.addEventListener(
    "click",
    showLatestRange
);


const resizeObserver =
    new ResizeObserver(
        (entries) => {
            const entry = entries[0];

            if (!entry) {
                return;
            }

            const {
                width,
                height,
            } = entry.contentRect;

            chart.resize(
                width,
                height
            );
        }
    );


resizeObserver.observe(
    chartContainer
);


window.addEventListener(
    "error",
    (event) => {
        console.error(
            "Global JavaScript error:",
            event.error
            || event.message
        );
    }
);


populateStockSelect();
loadSelectedKlineData();