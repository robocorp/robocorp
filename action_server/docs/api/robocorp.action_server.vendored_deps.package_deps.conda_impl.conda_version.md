<!-- markdownlint-disable -->

# module `robocorp.action_server.vendored_deps.package_deps.conda_impl.conda_version`

**Source:** [`conda_version.py:0`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L0)

Implements the version spec with parsing and comparison logic.

Object inheritance:

.. autoapi-inheritance-diagram:: BaseSpec VersionSpec BuildNumberMatch :top-classes: conda.models.version.BaseSpec:parts: 1

## Variables

- **version_cache**
- **VSPEC_TOKENS**
- **OPERATOR_MAP**
- **OPERATOR_START**

______________________________________________________________________

## function `normalized_version`

**Source:** [`conda_version.py:26`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L26)

```python
normalized_version(version: 'str') → 'VersionOrder'
```

Parse a version string and return VersionOrder object.

______________________________________________________________________

## function `ver_eval`

**Source:** [`conda_version.py:31`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L31)

```python
ver_eval(vtest, spec)
```

______________________________________________________________________

## function `treeify`

**Source:** [`conda_version.py:330`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L330)

```python
treeify(spec_str)
```

**Examples:**

` treeify("1.2.3")`
'1.2.3'
` treeify("1.2.3,>4.5.6")`(',', '1.2.3', '>4.5.6')
` treeify("1.2.3,4.5.6|<=7.8.9")`
('|', (',', '1.2.3', '4.5.6'), '\<=7.8.9')
` treeify("(1.2.3|4.5.6),<=7.8.9")`(',', ('|', '1.2.3', '4.5.6'), '\<=7.8.9')
` treeify("((1.5|((1.6|1.7), 1.8), 1.9 |2.0))|2.1")`
('|', '1.5', (',', ('|', '1.6', '1.7'), '1.8', '1.9'), '2.0', '2.1')
` treeify("1.5|(1.6|1.7),1.8,1.9|2.0|2.1")`('|', '1.5', (',', ('|', '1.6', '1.7'), '1.8', '1.9'), '2.0', '2.1')

______________________________________________________________________

## function `untreeify`

**Source:** [`conda_version.py:398`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L398)

```python
untreeify(spec, _inand=False, depth=0)
```

**Examples:**

` untreeify('1.2.3')`
'1.2.3'
` untreeify((',', '1.2.3', '>4.5.6'))`'1.2.3,>4.5.6'
` untreeify(('|', (',', '1.2.3', '4.5.6'), '<=7.8.9'))`
'(1.2.3,4.5.6)|\<=7.8.9'
` untreeify((',', ('|', '1.2.3', '4.5.6'), '<=7.8.9'))`'(1.2.3|4.5.6),\<=7.8.9'
` untreeify(('|', '1.5', (',', ('|', '1.6', '1.7'), '1.8', '1.9'), '2.0', '2.1'))`
'1.5|((1.6|1.7),1.8,1.9)|2.0|2.1'

______________________________________________________________________

## function `compatible_release_operator`

**Source:** [`conda_version.py:427`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L427)

```python
compatible_release_operator(x, y)
```

______________________________________________________________________

## exception `InvalidVersionSpec`

**Source:** [`conda_version.py:19`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L19)

______________________________________________________________________

## class `SingleStrArgCachingType`

**Source:** [`conda_version.py:40`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L40)

______________________________________________________________________

## class `VersionOrder`

**Source:** [`conda_version.py:54`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L54)

Implement an order relation between version strings.

Version strings can contain the usual alphanumeric characters (A-Za-z0-9), separated into components by dots and underscores. Empty segments (i.e. two consecutive dots, a leading/trailing underscore) are not permitted. An optional epoch number - an integer followed by '!' - can proceed the actual version string (this is useful to indicate a change in the versioning scheme itself). Version comparison is case-insensitive.

Conda supports six types of version strings: * Release versions contain only integers, e.g. '1.0', '2.3.5'. * Pre-release versions use additional letters such as 'a' or 'rc', for example '1.0a1', '1.2.beta3', '2.3.5rc3'.\* Development versions are indicated by the string 'dev', for example '1.0dev42', '2.3.5.dev12'.\* Post-release versions are indicated by the string 'post', for example '1.0post1', '2.3.5.post2'.\* Tagged versions have a suffix that specifies a particular property of interest, e.g. '1.1.parallel'. Tags can be addedto any of the preceding four types. As far as sorting is concerned,tags are treated like strings in pre-release versions.\* An optional local version string separated by '+' can be appended to the main (upstream) version string. It is only consideredin comparisons when the main versions are equal, but otherwisehandled in exactly the same manner.

To obtain a predictable version ordering, it is crucial to keep the version number scheme of a given package consistent over time. Specifically, * version strings should always have the same number of components (except for an optional tag suffix or local version string),\* letters/strings indicating non-release versions should always occur at the same position.

Before comparison, version strings are parsed as follows: * They are first split into epoch, version number, and local version number at '!' and '+' respectively. If there is no '!', the epoch isset to 0. If there is no '+', the local version is empty.\* The version part is then split into components at '.' and '\_'. * Each component is split again into runs of numerals and non-numerals * Subcomponents containing only numerals are converted to integers. * Strings are converted to lower case, with special treatment for 'dev' and 'post'.\* When a component starts with a letter, the fillvalue 0 is inserted to keep numbers and strings in phase, resulting in '1.1.a1' == 1.1.0a1'.\* The same is repeated for the local version part.

**Examples:**
1.2g.beta15.rc  =>  \[\[0\], \[1\], \[2, 'g'\], \[0, 'beta', 15\], \[0, 'rc'\]\]1!2.15.1_ALPHA  =>  \[\[1\], \[2\], \[15\], \[1, '\_alpha'\]\]

The resulting lists are compared lexicographically, where the following rules are applied to each pair of corresponding subcomponents: * integers are compared numerically * strings are compared lexicographically, case-insensitive * strings are smaller than integers, except * 'dev' versions are smaller than all corresponding versions of other types * 'post' versions are greater than all corresponding versions of other types * if a subcomponent has no correspondent, the missing correspondent is treated as integer 0 to ensure '1.1' == '1.1.0'.

The resulting order is: 0.4\< 0.4.0\< 0.4.1.rc== 0.4.1.RC   # case-insensitive comparison\< 0.4.1\< 0.5a1\< 0.5b3\< 0.5C1      # case-insensitive comparison\< 0.5\< 0.9.6\< 0.960923\< 1.0\< 1.1dev1    # special case 'dev'\< 1.1\_       # appended underscore is special case for openssl-like versions\< 1.1a1\< 1.1.0dev1  # special case 'dev'== 1.1.dev1   # 0 is inserted before string\< 1.1.a1\< 1.1.0rc1\< 1.1.0== 1.1\< 1.1.0post1 # special case 'post'== 1.1.post1  # 0 is inserted before string\< 1.1post1   # special case 'post'\< 1996.07.12\< 1!0.4.1    # epoch increased\< 1!3.1.1.6\< 2!0.4.1    # epoch increased again

Some packages (most notably openssl) have incompatible version conventions. In particular, openssl interprets letters as version counters rather than pre-release identifiers. For openssl, the relation

1.0.1 \< 1.0.1a  =>  False  # should be true for openssl

holds, whereas conda packages use the opposite ordering. You can work-around this problem by appending an underscore to plain version numbers:

1.0.1\_ \< 1.0.1a =>  True   # ensure correct ordering for openssl

### method `__init__`

**Source:** [`conda_version.py:161`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L161)

```python
__init__(vstr)
```

______________________________________________________________________

### method `startswith`

**Source:** [`conda_version.py:267`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L267)

```python
startswith(other)
```

______________________________________________________________________

## class `BaseSpec`

**Source:** [`conda_version.py:453`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L453)

### method `__init__`

**Source:** [`conda_version.py:454`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L454)

```python
__init__(spec_str, matcher, is_exact)
```

#### property `exact_value`

#### property `raw_value`

#### property `spec`

______________________________________________________________________

### method `all_match`

**Source:** [`conda_version.py:505`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L505)

```python
all_match(spec_str)
```

______________________________________________________________________

### method `always_true_match`

**Source:** [`conda_version.py:511`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L511)

```python
always_true_match(spec_str)
```

______________________________________________________________________

### method `any_match`

**Source:** [`conda_version.py:502`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L502)

```python
any_match(spec_str)
```

______________________________________________________________________

### method `exact_match`

**Source:** [`conda_version.py:508`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L508)

```python
exact_match(spec_str)
```

______________________________________________________________________

### method `is_exact`

**Source:** [`conda_version.py:463`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L463)

```python
is_exact()
```

______________________________________________________________________

### method `merge`

**Source:** [`conda_version.py:493`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L493)

```python
merge(other)
```

______________________________________________________________________

### method `operator_match`

**Source:** [`conda_version.py:499`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L499)

```python
operator_match(spec_str)
```

______________________________________________________________________

### method `regex_match`

**Source:** [`conda_version.py:496`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L496)

```python
regex_match(spec_str)
```

______________________________________________________________________

## class `VersionSpec`

**Source:** [`conda_version.py:515`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L515)

### method `__init__`

**Source:** [`conda_version.py:518`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L518)

```python
__init__(vspec)
```

#### property `exact_value`

#### property `raw_value`

#### property `spec`

______________________________________________________________________

### method `all_match`

**Source:** [`conda_version.py:505`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L505)

```python
all_match(spec_str)
```

______________________________________________________________________

### method `always_true_match`

**Source:** [`conda_version.py:511`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L511)

```python
always_true_match(spec_str)
```

______________________________________________________________________

### method `any_match`

**Source:** [`conda_version.py:502`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L502)

```python
any_match(spec_str)
```

______________________________________________________________________

### method `exact_match`

**Source:** [`conda_version.py:508`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L508)

```python
exact_match(spec_str)
```

______________________________________________________________________

### method `get_matcher`

**Source:** [`conda_version.py:522`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L522)

```python
get_matcher(vspec)
```

______________________________________________________________________

### method `is_exact`

**Source:** [`conda_version.py:463`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L463)

```python
is_exact()
```

______________________________________________________________________

### method `merge`

**Source:** [`conda_version.py:615`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L615)

```python
merge(other)
```

______________________________________________________________________

### method `operator_match`

**Source:** [`conda_version.py:499`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L499)

```python
operator_match(spec_str)
```

______________________________________________________________________

### method `regex_match`

**Source:** [`conda_version.py:496`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L496)

```python
regex_match(spec_str)
```

______________________________________________________________________

### method `union`

**Source:** [`conda_version.py:619`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L619)

```python
union(other)
```

______________________________________________________________________

## class `BuildNumberMatch`

**Source:** [`conda_version.py:627`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L627)

### method `__init__`

**Source:** [`conda_version.py:630`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L630)

```python
__init__(vspec)
```

#### property `exact_value`

#### property `raw_value`

#### property `spec`

______________________________________________________________________

### method `all_match`

**Source:** [`conda_version.py:505`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L505)

```python
all_match(spec_str)
```

______________________________________________________________________

### method `always_true_match`

**Source:** [`conda_version.py:511`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L511)

```python
always_true_match(spec_str)
```

______________________________________________________________________

### method `any_match`

**Source:** [`conda_version.py:502`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L502)

```python
any_match(spec_str)
```

______________________________________________________________________

### method `exact_match`

**Source:** [`conda_version.py:508`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L508)

```python
exact_match(spec_str)
```

______________________________________________________________________

### method `get_matcher`

**Source:** [`conda_version.py:634`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L634)

```python
get_matcher(vspec)
```

______________________________________________________________________

### method `is_exact`

**Source:** [`conda_version.py:463`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L463)

```python
is_exact()
```

______________________________________________________________________

### method `merge`

**Source:** [`conda_version.py:680`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L680)

```python
merge(other)
```

______________________________________________________________________

### method `operator_match`

**Source:** [`conda_version.py:499`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L499)

```python
operator_match(spec_str)
```

______________________________________________________________________

### method `regex_match`

**Source:** [`conda_version.py:496`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L496)

```python
regex_match(spec_str)
```

______________________________________________________________________

### method `union`

**Source:** [`conda_version.py:688`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_version.py#L688)

```python
union(other)
```
