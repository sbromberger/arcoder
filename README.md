# ARCoder

arcoder.py implements an abstract base class called `Encoder` along with two concrete
implementations: `ARCoder` and `Holmes`. Each has an `encode` method that takes a
string and encodes it into a series of symbols designed to be used for similarity
measurements.

```python
    >>> from arcoder import ARCoder, Holmes
    >>> a = ARCoder()
    >>> a.encode("Sohaib")
    ['suhaeb', 'suhib']
    >>> h = Holmes()
    >>> h.encode("Sohaib")
    ['sohayb']
```

The ARCoder algorithm is described more fully in
Moore, J., Hamid, S., and Bromberger, S., "An Evaluation of Transliterated
Arabic Name Matching Methods".

The Holmes implementation is derived from
Holmes, D., Kashfi, S., Aqeel, S. U.: "Transliterated arabic name search",
_Communications, Internet, and Information Technology_, pp. 267-273. (2004).

