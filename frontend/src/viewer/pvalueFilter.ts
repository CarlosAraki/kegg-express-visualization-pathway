const PVALUE_SLIDER_STEPS = 1000;
const PVALUE_PAD = 0.01e-5;

export interface PvalueFilterConfig {
  dataMin: number;
  dataMax: number;
}

export interface PvalueRange {
  min: number;
  max: number;
}

export function getFilterBounds(config: PvalueFilterConfig) {
  const filterMin = Math.max(0, config.dataMin - PVALUE_PAD);
  const filterMax = config.dataMax + PVALUE_PAD;
  return { filterMin, filterMax, pad: PVALUE_PAD };
}

export function sliderToPvalue(
  step: number,
  filterMin: number,
  filterMax: number,
): number {
  const lo = Math.log10(filterMin || 1e-12);
  const hi = Math.log10(filterMax || 1);
  const t = step / PVALUE_SLIDER_STEPS;
  return 10 ** (lo + t * (hi - lo));
}

export function formatPvalue(value: number): string {
  if (value < 0.001) return value.toExponential(2);
  return value.toFixed(4);
}

export function createPvalueFilter(
  config: PvalueFilterConfig,
  elements: {
    minInput: HTMLInputElement;
    maxInput: HTMLInputElement;
    minLabel: HTMLElement;
    maxLabel: HTMLElement;
    count: HTMLElement;
    reset: HTMLButtonElement;
  },
  onChange: (range: PvalueRange) => void,
) {
  const { filterMin, filterMax } = getFilterBounds(config);

  elements.minInput.min = "0";
  elements.minInput.max = String(PVALUE_SLIDER_STEPS);
  elements.minInput.value = "0";
  elements.maxInput.min = "0";
  elements.maxInput.max = String(PVALUE_SLIDER_STEPS);
  elements.maxInput.value = String(PVALUE_SLIDER_STEPS);

  const updateLabels = () => {
    elements.minLabel.textContent = formatPvalue(
      sliderToPvalue(Number(elements.minInput.value), filterMin, filterMax),
    );
    elements.maxLabel.textContent = formatPvalue(
      sliderToPvalue(Number(elements.maxInput.value), filterMin, filterMax),
    );
  };

  const getRange = (): PvalueRange => ({
    min: sliderToPvalue(Number(elements.minInput.value), filterMin, filterMax),
    max: sliderToPvalue(Number(elements.maxInput.value), filterMin, filterMax),
  });

  const apply = () => {
    updateLabels();
    onChange(getRange());
  };

  elements.minInput.addEventListener("input", () => {
    if (Number(elements.minInput.value) > Number(elements.maxInput.value)) {
      elements.minInput.value = elements.maxInput.value;
    }
    apply();
  });

  elements.maxInput.addEventListener("input", () => {
    if (Number(elements.maxInput.value) < Number(elements.minInput.value)) {
      elements.maxInput.value = elements.minInput.value;
    }
    apply();
  });

  elements.reset.addEventListener("click", () => {
    elements.minInput.value = "0";
    elements.maxInput.value = String(PVALUE_SLIDER_STEPS);
    apply();
  });

  apply();

  return {
    getRange,
    setCount(visible: number, total: number) {
      elements.count.textContent = `${visible} / ${total} bars visible`;
    },
  };
}
