MathJax.Hub.Config({
        extensions: ["tex2jax.js","TeX/AMSmath.js","TeX/AMSsymbols.js"],
        jax: ["input/TeX", "output/HTML-CSS"],
        tex2jax: {
            inlineMath: [ ['$','$'], ["\\(","\\)"] ],
            displayMath: [ ['$$','$$'], ["\\[","\\]"] ],
            processEscapes: false,
            element: "content",
            ignoreClass: "(tex2jax_ignore|mw-search-results|searchresults)", /* note: this is part of a regex, check the docs! */
            skipTags: ["script","noscript","style","textarea","code"] /* removed pre as wikimedia renders math in there */
        },
        /* "HTML-CSS": { availableFonts: ["TeX"] }, */
        TeX: {
          Macros: {
            /* Wikipedia compatibility: these macros are used on Wikipedia */
            empty: '\\emptyset',
            P: '\\unicode{xb6}',
            Alpha: '\\unicode{x391}', /* FIXME: These capital Greeks don't show up in bold in \boldsymbol ... */
            Beta: '\\unicode{x392}',
            Epsilon: '\\unicode{x395}',
            Zeta: '\\unicode{x396}',
            Eta: '\\unicode{x397}',
            Iota: '\\unicode{x399}',
            Kappa: '\\unicode{x39a}',
            Mu: '\\unicode{x39c}',
            Nu: '\\unicode{x39d}',
            Pi: '\\unicode{x3a0}',
            Rho: '\\unicode{x3a1}',
            Sigma: '\\unicode{x3a3}',
            Tau: '\\unicode{x3a4}',
            Chi: '\\unicode{x3a7}',
            C: '\\mathbb{C}',        /* the complex numbers */
            N: '\\mathbb{N}',        /* the natural numbers */
            Q: '\\mathbb{Q}',        /* the rational numbers */
            R: '\\mathbb{R}',        /* the real numbers */
            Z: '\\mathbb{Z}',        /* the integer numbers */
 
            /* some extre macros for ease of use; these are non-standard! */
            F: '\\mathbb{F}',        /* a finite field */
            HH: '\\mathcal{H}',      /* a Hilbert space */
            bszero: '\\boldsymbol{0}', /* vector of zeros */
            bsone: '\\boldsymbol{1}',  /* vector of ones */
            bst: '\\boldsymbol{t}',    /* a vector 't' */
            bsv: '\\boldsymbol{v}',    /* a vector 'v' */
            bsw: '\\boldsymbol{w}',    /* a vector 'w' */
            bsx: '\\boldsymbol{x}',    /* a vector 'x' */
            bsy: '\\boldsymbol{y}',    /* a vector 'y' */
            bsz: '\\boldsymbol{z}',    /* a vector 'z' */
            bsDelta: '\\boldsymbol{\\Delta}', /* a vector '\Delta' */
            E: '\\mathrm{e}',          /* the exponential */
            rd: '\\,\\mathrm{d}',      /*  roman d for use in integrals: $\int f(x) \rd x$ */
            rdelta: '\\,\\delta',      /* delta operator for use in sums */
            rD: '\\mathrm{D}',         /* differential operator D */
 
            /* example from MathJax on how to define macros with parameters: */
            /* bold: ['{\\bf #1}', 1] */
 
            RR: '\\mathbb{R}',
            ZZ: '\\mathbb{Z}',
            NN: '\\mathbb{N}',
            QQ: '\\mathbb{Q}',
            CC: '\\mathbb{C}',
            FF: '\\mathbb{F}'
          }
        }
    });