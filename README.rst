Mathics3 Module for ICU — International Components for Unicode

Functions that provide information from the `Python ICU library <https://pypi.org/project/pyicu/>`_.

Example Session
---------------

::

   $ mathicsscript
   In[1]:= LoadModule["pymathics.icu"]
   Out[1]= pymathics.icu

   In[2]= Alphabet["Croatian"]
   Out[2]= {a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, r, s, t, u, v, z, ć, č, đ, š, ž, dž, lj, nj}

   In[3]:= $Language
   Out[3]= "English"

   In[4]:= Alphabet[]
   Out[4]= {a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z}

   In[5]:= $Language="German"
   Out[5]= "German"

   In[6]:= Alphabet[]
   Out[6]= {a, ä, b, c, d, e, f, g, h, i, j, k, l, m, n, o, ö, p, q, r, s, ß, t, u, ü, v, w, x, y, z}

   In[7]:= AlphabeticOrder["Papá", "Papagayo", "Spanish"]
   Out[7]= 1

   In[8]:= AlphabeticOrder["Papá", "Papa", "Spanish"]
   Out[8]= -1

   In[8]:= AlphabeticOrder["Papá", ""Papá", "Spanish"]
   Out[8]= 0
