# mezzacotta Generator

Source code for the [mezzacotta Generator](http://www.mezzacotta.net/generate/) web page and family of random text generators.

Unlike the predecessors, [mezzacotta Cafe](https://github.com/dmmaus/mezzacotta-cafe) and [mezzacotta Cinematique](https://github.com/dmmaus/mezzacotta-cinematique), this code is designed to be fully generic, extensible, and customisable to any random text generation context, with a common core of categorised vocabulary files.

## Contributing

Contributors are welcome to submit extensions to the menu generating source text files and grammar.

* Fork this repository, add your additions, and submit a pull request.
* You can run each subdirectory's index.php to generate a page of random text, however given the random nature of the generator it may take several runs to see the effects of your changes.

## Authors

* **[Andrew Coker](https://github.com/voidstaroz)** - *Initial work in Python*
* **[David Morgan-Mar](https://github.com/dmmaus)** - *PHP, HTML, and Python modifications*

See also the list of [contributors](https://github.com/dmmaus/mezzacotta-generator/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details

# Documentation

* Core shareable vocabulary files are in the directory `vocabulary`.
* Other directories contain specific generators with PHP index file, base grammar file, and context-dependent vocabulary files (of limited use to other generators).

## Running the generators

The Python generator code `generique.py` takes two or more arguments:

1. The first *N*-1 arguments are base vocabulary file name paths, without the `.txt` extension. These specify which text generators to run. If more than one base file is given, the outputs of the base files are concatenated with a `~~` separator.
1. The final argument is the number of lines of text to generate.

**From a web browser:** Place the code into your web server directory, then point your browser at the top level `index.php` file. Your web server will need to allow shell execution of Python from within PHP. You may ned to edit the python path in the subdirectory `index.php` files. The PHP code calls the Python `generique.py` to generate a number of lines, formatted for browser display.

**From the command line:** The `generique.py` script assumes that it is being called from a subdirectory. Change to a generator subdirectory (e.g. `<subdir>` = `test` or `tavern`) and run either:

* `python ../generique.py <subdir>/base <numlines>`
* `php index.php`

## Vocabulary file specification

All vocabulary files (including the base vocabulary file) are text files assumed to have `.txt` extensions. Vocabulary files may contain the following:

* **Comments.** Lines starting with a `#` character are comments, ignored by the parser.
* **Format specifier.** A line starting with `@format` is a format specifier. See "Format specifiers" below.
* **Case specifier.** A line specifying how returned text from the current file is to be capitalised. See "Case specifiers" below.
* **Quotation specifier.** A line starting with `@quoted` gives a numerical probability that strings returned by the current file will be enclosed in quote marks. Useful if you want "scare quotes" around stuff.
* **Included files.** A line starting with `@include` loads the following file, as if it were reproduced in full within the current file. The parser checks that the `@format` specifier is the same, otherwise throws an error.
* **Text, possibly with substitution strings.** Either vocabulary words, or substitution strings starting with a dollar sign. See "Text substitution" below.

### Format specifiers

These are lines starting with `@format`. They tell the parser the format of inflected forms of words in the file. Examples:

* `@format ~` - None of the following text has inflected word forms. Each line is printed as-is.
* `@format ~|S` - The following lines of text may occur in two different inflected forms, as-is, and a form which defaults to as-is concatenated with a letter 's' at the end. This is typical of nouns, and provides a plural form. (Some nouns pluralise in a different way, see below for details.)
* `@format ~|ER|EST` - Three inflected forms, suitable for adjectives with comparative and superlative forms. e.g. {smart, smarter, smartest}. The default comparative is formed by adding 'er' to the end of the word, and the default superlative by adding 'est' to the end of the word. (Some adjectives form comparatives and superlatives in a different way, see below for details.)
* `@format ~|S|ED|ING` Four inflected forms, suitable for verb tenses. e.g. {walk, walks, walked, walking}. (Some verbs are irregular, see below for details.)

Example text lines in various formats:

* `dog` - A noun with a regular plural (`dogs`). The plural does not need to be specified.
* `fox|foxes`, `mouse|mice`, `fish|fish` - Nouns with an irregular plural.
* `|butter` - Noun with no plural form (a mass noun). This syntax ignores all inflections and always returns the word as given.
* `smart` - An adjective with regular comparative and superlative forms.
* `big|bigger|biggest`, `bad|worse|worst`, `orange|more_orange|most_orange` - Adjectives with irregular comparative and superlative forms.
* `walk` - A regular verb with fully regular endings.
* `love|loves|loved|loving`, `eat|eats|ate|eating`, `have|has|had|having` - Irregular verbs.

### Case specifiers

These specify how text should be capitalised. A specifier in a given file capitalises the strings it returns (including text generated  by called files lower down the recursion stack), but does not affect text generated by calling files (further up the stack). This enables having text generated with subsections having specific capitalisation. e.g. "The adventurers found the Sword of Truth."

The only case specifier supported so far is:

* `@titlecase`. This specifies that strings returned by the current file will be capitalised in [Title Case](https://en.wiktionary.org/wiki/title_case).

## Text substitution

Text lines may contain words starting with dollar signs. These indicate substitution strings. Example:

* `the $noun` - The parser returns the word `the` followed by a random selection from the vocabulary file `noun.txt`.
* `the $noun_S` - The parser returns the word `the` followed by *the plural form* of a random selection from the vocabulary file `noun.txt`.
* `a $adjective $noun` - The parser returns the word `a` followed by a random selection from the vocabulary file `adjective.txt` followed by a random selection from the vocabulary file `noun.txt`.
* `a $adjective_ER $noun` - The parser returns the word `a` followed by *the comparative form* of a random selection from the vocabulary file `adjective.txt` followed by a random selection from the vocabulary file `noun.txt`.
* `a $adjective_EST $noun` - The parser returns the word `a` followed by *the superlative form* of a random selection from the vocabulary file `adjective.txt` followed by a random selection from the vocabulary file `noun.txt`.
* etc.

The parser recursively generates random strings from referenced files until it bottoms out, and then returns the entire generated string.

There are also special @-commands that produce substituted text:

* `@recentyearN` - Generates a year number in the past, biased towards more recent years, and substitutes it in place. `N` is a number, which is interpreted as a scale factor for the logarithmic probability distribution. Most years generated will be within *N* yers of the present, but there is a long low probability tail.

### Conditional substitution

A dollar sign may be preceded by a digit (1-9). This indicates that the attached substitution string will only be included with probability (digit/10). The script generates a random number between 0 and 1, if it is greater than the probability, then the attached substitution is skipped. This is useful for additional words such as adjectives that you only want to include sometimes, allowing you to tune the frequency of inclusion.

If the substitution string is followed by a `>` character and alternate text, the text following the `>` is treated as an "else" string, and returned if the first substitution is not selected. For example:

* `with 3$number>a thousand meeples` - 30% of the time will return "with three [or some other number from number.txt] thousand meeples" and 70% of the time will return "with a thousand meeples".

### Automatic substitutions

As a final pass, there are some automatic string substitutions made to tidy up the generated text.

* If the parser generates the word `a` followed by a word that starts with a vowel, it automatically converts `a` to `an`.
* Underscores are converted to spaces. (Underscores are sometimes needed in vocabulary files to separate compound words with inflected forms, otherwise the inflection parsing gets confused.)
* Spaces around hyphens are removed. This is so you can specify prefixes and suffixes with hyphens. For example, `super-` as an adjective, and have the string `super-badger` returned without a space after the hyphen.
* Plus signs and spaces around them are removed. This is so you can specify prefixes and suffixes that join onto words without hyphens. For example, `super+` as an adjective, and have the string `superbadger` returned without a space or hyphen.
* Spaces before certain punctuation (`. , ? ! ' : ; )`) and spaces after open parentheses (`(`) are removed.
* Doubled up punctuation is reduced to a single punctuation character. Conflicting punctuation is resolved to the "strongest" character - e.g. `.!` becomes `!`.

### The difference between includes and substitutions

Example: If we have two text files:

```
# dinosaur.txt
@format ~|S
diplodocus|diplodocuses
Tyrannosaurus rex|rexes

# mammal.txt
@format ~|S
cat
dog
horse
rabbit
```

And we want to make a file `animal.txt` that could select either dinosaurs or mammals, we could do either:

```
# animal.txt
@format ~|S
$dinosaur
$mammal
```

which would select a dinosaur 50% of the time and a mammal 50% of the time (i.e. diplodocus and T. Rex have probability 1/4, while cat, dog, horse, and rabbit all have probability 1/8), or:

```
# animal.txt
@format ~|S
@include dinosaur
@include mammal
```

which would select each animal with equal probability 1/6.

## PHP

The sample PHP code does the following substitutions:

* Apostrophes are replaced with curly apostrophes.
* `dish/index.php` shows an example of HTML formatting output from multiple base generators in a single Python call.

