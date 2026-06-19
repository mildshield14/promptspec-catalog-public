(function () {
  "use strict";

  var REPOSITORY_URL = "https://github.com/mildshield14/promptspec-catalog-public";
  var RAW_CATALOG_URL =
    "https://raw.githubusercontent.com/mildshield14/promptspec-catalog-public/main/catalog/patterns.json";
  var CATALOG_PATHS = ["../catalog/patterns.json", "catalog/patterns.json", RAW_CATALOG_URL];

  var state = {
    patterns: [],
    filtered: [],
    search: "",
    category: "",
    sourceStatus: "",
    hasSourceStatus: false
  };

  var elements = {
    count: document.getElementById("pattern-count"),
    grid: document.getElementById("pattern-grid"),
    empty: document.getElementById("empty-state"),
    message: document.getElementById("load-message"),
    search: document.getElementById("search-input"),
    category: document.getElementById("category-filter"),
    sourceStatusField: document.getElementById("source-status-field"),
    sourceStatus: document.getElementById("source-status-filter")
  };

  function text(value) {
    if (value === null || value === undefined) {
      return "";
    }
    if (Array.isArray(value)) {
      return value.filter(Boolean).join(", ");
    }
    return String(value);
  }

  function normalizeCategory(value) {
    return text(value)
      .toLowerCase()
      .split("_")
      .filter(Boolean)
      .map(function (part) {
        return part.charAt(0).toUpperCase() + part.slice(1);
      })
      .join(" ");
  }

  function uniqueValues(patterns, key) {
    var seen = {};
    patterns.forEach(function (pattern) {
      var value = text(pattern[key]).trim();
      if (value) {
        seen[value] = true;
      }
    });
    return Object.keys(seen).sort();
  }

  function setMessage(message, isError) {
    if (!message) {
      elements.message.classList.add("hidden");
      elements.message.textContent = "";
      return;
    }
    elements.message.textContent = message;
    elements.message.classList.remove("hidden");
    elements.message.classList.toggle("error", Boolean(isError));
  }

  function createElement(tag, className, content) {
    var element = document.createElement(tag);
    if (className) {
      element.className = className;
    }
    if (content !== undefined && content !== null) {
      element.textContent = content;
    }
    return element;
  }

  function appendDetail(parent, label, value, asPre) {
    var body = text(value).trim();
    if (!body) {
      return;
    }

    var block = createElement("div", "detail-block");
    block.appendChild(createElement("span", "detail-label", label));
    block.appendChild(asPre ? createElement("pre", "", body) : createElement("p", "meta-text", body));
    parent.appendChild(block);
  }

  function populateSelect(select, values, labelFormatter) {
    values.forEach(function (value) {
      var option = document.createElement("option");
      option.value = value;
      option.textContent = labelFormatter ? labelFormatter(value) : value;
      select.appendChild(option);
    });
  }

  function renderFilters() {
    populateSelect(elements.category, uniqueValues(state.patterns, "category"), normalizeCategory);

    var sourceStatuses = uniqueValues(state.patterns, "sourceStatus");
    state.hasSourceStatus = sourceStatuses.length > 0;
    if (state.hasSourceStatus) {
      populateSelect(elements.sourceStatus, sourceStatuses);
      elements.sourceStatusField.classList.remove("hidden");
    }
  }

  function patternMatches(pattern) {
    var query = state.search.trim().toLowerCase();
    var haystack = [
      pattern.name,
      pattern.description,
      pattern.detectionInstruction,
      pattern.notes,
      pattern.aliases,
      pattern.category,
      pattern.sourceStatus
    ]
      .map(text)
      .join(" ")
      .toLowerCase();

    if (query && haystack.indexOf(query) === -1) {
      return false;
    }
    if (state.category && text(pattern.category) !== state.category) {
      return false;
    }
    if (state.sourceStatus && text(pattern.sourceStatus) !== state.sourceStatus) {
      return false;
    }
    return true;
  }

  function renderCard(pattern) {
    var card = createElement("article", "pattern-card");
    card.setAttribute("aria-labelledby", pattern.id ? "pattern-" + pattern.id : "");

    var head = createElement("div", "card-head");
    var title = createElement("h3", "", text(pattern.name) || "Untitled pattern");
    if (pattern.id) {
      title.id = "pattern-" + pattern.id;
    }
    head.appendChild(title);

    if (pattern.category) {
      var tags = createElement("ul", "tag-list");
      var tag = createElement("li", "tag", normalizeCategory(pattern.category));
      tags.appendChild(tag);
      head.appendChild(tags);
    }
    card.appendChild(head);

    card.appendChild(createElement("p", "description", text(pattern.description) || "No description provided."));

    if (pattern.detectionInstruction) {
      var cue = createElement("p", "cue");
      cue.appendChild(createElement("strong", "", "Cue: "));
      cue.appendChild(document.createTextNode(text(pattern.detectionInstruction)));
      card.appendChild(cue);
    }

    if (pattern.sourceStatus) {
      var status = createElement("p", "meta-text");
      status.appendChild(createElement("strong", "", "Source status: "));
      status.appendChild(document.createTextNode(text(pattern.sourceStatus)));
      card.appendChild(status);
    }

    if (pattern.aliases || pattern.notes) {
      var meta = createElement("p", "meta-text");
      if (pattern.aliases) {
        meta.appendChild(createElement("strong", "", "Aliases: "));
        meta.appendChild(document.createTextNode(text(pattern.aliases)));
      } else {
        meta.appendChild(createElement("strong", "", "Notes: "));
        meta.appendChild(document.createTextNode(text(pattern.notes)));
      }
      card.appendChild(meta);
    }

    var details = document.createElement("details");
    var summary = document.createElement("summary");
    summary.textContent = "View details";
    details.appendChild(summary);

    var detailBody = createElement("div", "details-body");
    appendDetail(detailBody, "Description", pattern.description, false);
    appendDetail(detailBody, "Detection instruction", pattern.detectionInstruction, false);
    appendDetail(detailBody, "Placeholder form", pattern.placeholderExample, true);
    appendDetail(detailBody, "Example", pattern.example, true);
    appendDetail(detailBody, "Notes", pattern.notes, false);
    details.appendChild(detailBody);
    card.appendChild(details);

    return card;
  }

  function renderPatterns() {
    state.filtered = state.patterns.filter(patternMatches);
    elements.grid.textContent = "";

    state.filtered.forEach(function (pattern) {
      elements.grid.appendChild(renderCard(pattern));
    });

    elements.empty.classList.toggle("hidden", state.filtered.length > 0);
    elements.count.textContent =
      state.filtered.length === state.patterns.length
        ? state.patterns.length + " patterns"
        : state.filtered.length + " of " + state.patterns.length + " patterns";
  }

  function wireControls() {
    document.querySelectorAll('a[aria-disabled="true"]').forEach(function (link) {
      link.addEventListener("click", function (event) {
        event.preventDefault();
      });
    });

    elements.search.addEventListener("input", function (event) {
      state.search = event.target.value;
      renderPatterns();
    });

    elements.category.addEventListener("change", function (event) {
      state.category = event.target.value;
      renderPatterns();
    });

    elements.sourceStatus.addEventListener("change", function (event) {
      state.sourceStatus = event.target.value;
      renderPatterns();
    });
  }

  function fetchCatalogFrom(paths) {
    var failures = [];

    function tryPath(index) {
      if (index >= paths.length) {
        throw new Error("Could not load catalog JSON. Tried: " + failures.join(", "));
      }

      return fetch(paths[index], { cache: "no-store" })
        .then(function (response) {
          if (!response.ok) {
            throw new Error(paths[index] + " returned " + response.status);
          }
          return response.json();
        })
        .catch(function (error) {
          failures.push(error.message);
          return tryPath(index + 1);
        });
    }

    return tryPath(0);
  }

  function init() {
    setMessage("Loading catalog from patterns.json...", false);
    fetchCatalogFrom(CATALOG_PATHS)
      .then(function (data) {
        if (!data || !Array.isArray(data.patterns)) {
          throw new Error("Catalog JSON did not contain a patterns array.");
        }
        state.patterns = data.patterns.slice();
        renderFilters();
        wireControls();
        renderPatterns();
        setMessage("", false);
      })
      .catch(function (error) {
        elements.count.textContent = "Catalog unavailable";
        setMessage(
          "The interactive catalog could not be loaded. Read the JSON source or Markdown catalog from the repository instead. " +
            error.message,
          true
        );
      });
  }

  init();
})();
