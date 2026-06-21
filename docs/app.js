(function () {
  "use strict";

  var CATALOG_PATHS = ["../catalog/patterns.json", "catalog/patterns.json"];

  var CATEGORY_ORDER = [
    "IN_CONTEXT_LEARNING",
    "REASONING",
    "OUTPUT_CONTROL",
    "CONTEXT_CONTROL",
    "META_DIRECTIVES"
  ];

  var CATEGORY_LABELS = {
    IN_CONTEXT_LEARNING: "In-Context Learning",
    REASONING: "Reasoning",
    OUTPUT_CONTROL: "Output Control",
    CONTEXT_CONTROL: "Context Control",
    META_DIRECTIVES: "Meta-Directives"
  };

  var COMPONENT_LABELS = {
    PROFILE_ROLE: "Profile/Role",
    DIRECTIVE: "Directive",
    CONTEXT: "Context",
    PROCEDURAL_STEPS: "Procedural Steps",
    EXAMPLES: "Examples",
    OUTPUT_FORMAT: "Output Format/Style",
    CONSTRAINTS: "Constraints"
  };

  var state = {
    patterns: [],
    filtered: [],
    search: "",
    expanded: {}
  };

  var elements = {
    count: document.getElementById("pattern-count"),
    tree: document.getElementById("taxonomy-tree"),
    empty: document.getElementById("empty-state"),
    message: document.getElementById("load-message"),
    search: document.getElementById("search-input")
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

  function labelCategory(value) {
    return CATEGORY_LABELS[value] || text(value);
  }

  function labelComponent(value) {
    return COMPONENT_LABELS[value] || text(value);
  }

  function slug(value) {
    return text(value)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");
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

  function buttonNode(label, count, level, key, expanded) {
    var button = createElement("button", "tree-toggle level-" + level);
    var panelId = "panel-" + slug(key);
    button.type = "button";
    button.dataset.toggleKey = key;
    button.setAttribute("aria-expanded", expanded ? "true" : "false");
    button.setAttribute("aria-controls", panelId);

    button.appendChild(createElement("span", "toggle-mark", expanded ? "-" : "+"));
    button.appendChild(createElement("span", "node-label", label));
    if (count !== null && count !== undefined) {
      button.appendChild(createElement("span", "node-count", String(count)));
    }
    return button;
  }

  function panelNode(key, expanded) {
    var panel = createElement("div", "tree-panel");
    panel.id = "panel-" + slug(key);
    panel.hidden = !expanded;
    return panel;
  }

  function patternHaystack(pattern) {
    return [
      pattern.name,
      pattern.description,
      pattern.subcategory,
      pattern.category,
      pattern.componentTypes,
      pattern.detectionInstruction,
      pattern.notes
    ]
      .map(text)
      .join(" ")
      .toLowerCase();
  }

  function patternMatches(pattern) {
    var query = state.search.trim().toLowerCase();
    if (!query) {
      return true;
    }
    return patternHaystack(pattern).indexOf(query) !== -1;
  }

  function groupPatterns(patterns) {
    var grouped = {};
    patterns.forEach(function (pattern) {
      var category = pattern.category || "UNCATEGORIZED";
      var subcategory = pattern.subcategory || "Uncategorized";
      grouped[category] = grouped[category] || {};
      grouped[category][subcategory] = grouped[category][subcategory] || [];
      grouped[category][subcategory].push(pattern);
    });
    Object.keys(grouped).forEach(function (category) {
      Object.keys(grouped[category]).forEach(function (subcategory) {
        grouped[category][subcategory].sort(function (a, b) {
          return text(a.name).localeCompare(text(b.name));
        });
      });
    });
    return grouped;
  }

  function countCategory(subgroups) {
    return Object.keys(subgroups).reduce(function (total, subcategory) {
      return total + subgroups[subcategory].length;
    }, 0);
  }

  function isExpanded(key, defaultValue, forceExpanded) {
    if (forceExpanded) {
      return true;
    }
    if (Object.prototype.hasOwnProperty.call(state.expanded, key)) {
      return state.expanded[key];
    }
    return defaultValue;
  }

  function renderComponentTags(pattern) {
    var tags = createElement("ul", "tag-list");
    (pattern.componentTypes || []).forEach(function (component) {
      tags.appendChild(createElement("li", "tag", labelComponent(component)));
    });
    return tags;
  }

  function renderPatternDetails(pattern) {
    var details = createElement("div", "pattern-details");

    var componentBlock = createElement("div", "detail-block");
    componentBlock.appendChild(createElement("span", "detail-label", "Component use"));
    componentBlock.appendChild(renderComponentTags(pattern));
    details.appendChild(componentBlock);

    var description = createElement("div", "detail-block");
    description.appendChild(createElement("span", "detail-label", "Description"));
    description.appendChild(createElement("p", "meta-text", text(pattern.description)));
    details.appendChild(description);

    if (pattern.formalization) {
      var formalization = createElement("div", "detail-block");
      formalization.appendChild(createElement("span", "detail-label", "Formalization"));
      formalization.appendChild(createElement("pre", "", text(pattern.formalization)));
      details.appendChild(formalization);
    }

    return details;
  }

  function renderPattern(pattern, queryActive) {
    var key = "pattern:" + pattern.id;
    var expanded = isExpanded(key, false, queryActive);
    var item = createElement("div", "tree-item pattern-item");
    item.appendChild(buttonNode(text(pattern.name), null, "pattern", key, expanded));

    var panel = panelNode(key, expanded);
    panel.appendChild(renderPatternDetails(pattern));
    item.appendChild(panel);
    return item;
  }

  function renderTree() {
    state.filtered = state.patterns.filter(patternMatches);
    var queryActive = Boolean(state.search.trim());
    var grouped = groupPatterns(state.filtered);
    var categories = CATEGORY_ORDER.filter(function (category) {
      return grouped[category];
    }).concat(
      Object.keys(grouped)
        .filter(function (category) {
          return CATEGORY_ORDER.indexOf(category) === -1;
        })
        .sort()
    );

    elements.tree.textContent = "";
    categories.forEach(function (category) {
      var subgroups = grouped[category];
      var categoryKey = "category:" + category;
      var categoryExpanded = isExpanded(categoryKey, true, queryActive);
      var categoryItem = createElement("section", "tree-item category-item");
      categoryItem.appendChild(
        buttonNode(labelCategory(category), countCategory(subgroups), "category", categoryKey, categoryExpanded)
      );

      var categoryPanel = panelNode(categoryKey, categoryExpanded);
      Object.keys(subgroups)
        .sort()
        .forEach(function (subcategory) {
          var patterns = subgroups[subcategory];
          var subcategoryKey = categoryKey + ":subcategory:" + subcategory;
          var subcategoryExpanded = isExpanded(subcategoryKey, false, queryActive);
          var subcategoryItem = createElement("div", "tree-item subcategory-item");
          subcategoryItem.appendChild(
            buttonNode(subcategory, patterns.length, "subcategory", subcategoryKey, subcategoryExpanded)
          );

          var subcategoryPanel = panelNode(subcategoryKey, subcategoryExpanded);
          patterns.forEach(function (pattern) {
            subcategoryPanel.appendChild(renderPattern(pattern, queryActive));
          });
          subcategoryItem.appendChild(subcategoryPanel);
          categoryPanel.appendChild(subcategoryItem);
        });
      categoryItem.appendChild(categoryPanel);
      elements.tree.appendChild(categoryItem);
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
      renderTree();
    });

    elements.tree.addEventListener("click", function (event) {
      var button = event.target.closest("button[data-toggle-key]");
      if (!button) {
        return;
      }
      var key = button.dataset.toggleKey;
      state.expanded[key] = button.getAttribute("aria-expanded") !== "true";
      renderTree();
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
        wireControls();
        renderTree();
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
