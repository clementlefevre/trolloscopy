Ab = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.";

var ab = function(a) {
        for (var b = [], c = 0, d = 0; d < a.length; d++) {
            for (var f = a.charCodeAt(d); 255 < f; )
                b[c++] = f & 255,
                f >>= 8;
            b[c++] = f
        }
        return b
    };

var ea = function(a) {
        var b = da(a);
        return "array" == b || "object" == b && "number" == typeof a.length
    };

var da = function(a) {
    var b = typeof a;
    if ("object" == b)
        if (a) {
            if (a instanceof Array)
                return "array";
            if (a instanceof Object)
                return b;
            var c = Object.prototype.toString.call(a);
            if ("[object Window]" == c)
                return "object";
            if ("[object Array]" == c || "number" == typeof a.length && "undefined" != typeof a.splice && "undefined" != typeof a.propertyIsEnumerable && !a.propertyIsEnumerable("splice"))
                return "array";
            if ("[object Function]" == c || "undefined" != typeof a.call && "undefined" != typeof a.propertyIsEnumerable && !a.propertyIsEnumerable("call"))
                return "function"
        } else
            return "null";
    else if ("function" == b && "undefined" == typeof a.call)
        return "object";
    return b
}
;

var wb = function() {
        
            yb = {};
            zb = {};
            xb = {};
            for (var a = 0; 65 > a; a++)
                yb[a] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/\x3d".charAt(a),
                zb[yb[a]] = a,
                xb[a] = Ab.charAt(a),
                62 <= a && (zb[Ab.charAt(a)] = a)
        
    }
    ;  

var vb = function(a) {
        a = ab(a);
        if (!ea(a))
            throw Error("encodeByteArray takes an array as a parameter");
        wb();
        for (var b = xb, c = [], d = 0; d < a.length; d += 3) {
            var f = a[d]
              , g = d + 1 < a.length
              , h = g ? a[d + 1] : 0
              , k = d + 2 < a.length
              , m = k ? a[d + 2] : 0
              , q = f >> 2
              , f = (f & 3) << 4 | h >> 4
              , h = (h & 15) << 2 | m >> 6
              , m = m & 63;
            k || (m = 64,
            g || (h = 64));
            c.push(b[q], b[f], b[h], b[m])
        }
        return c.join("")
    }
;


// console.log(vb("42ec5f88-8620-11e6-a29c-6e7d9515ad15"))