import glob
from os.path import join, split, abspath
import urllib.parse as parseurl
import numpy as np


def atomtype(structure, forcefield, non_atomistic=False, **kwargs):
    """Compare known atomtypes to those generated by foyer.

    Parameters
    ----------
    structure : parmed.Structure
        A parmed structure with `atom.type` attributes.
    forcefield : foyer.Forcefield
        A forcefield to use for atomtyping.

    Raises
    ------
    AssertionError

    """
    known_types = [atom.type for atom in structure.atoms]

    if non_atomistic:
        for atom in structure.atoms:
            atom.element = atom.name

    typed_structure = forcefield.apply(structure, **kwargs)

    generated_atom_types = list()
    for i, atom in enumerate(typed_structure.atoms):
        message = ('Found multiple or no atom types for atom {} in {}: {}\n'
                   'Should be atomtype: {}'.format(
            i, structure.title, atom.type, known_types[i]))
        assert atom.type, message
        generated_atom_types.append(atom.type)

    both = zip(generated_atom_types, known_types)

    n_types = np.array(range(len(generated_atom_types)))
    known_types = np.array(known_types)
    generated_atom_types = np.array(generated_atom_types)

    non_matches = np.array([a != b for a, b in both])
    message = "Found inconsistent atom types in {}: {}".format(
        structure.title,
        list(zip(n_types[non_matches],
                 generated_atom_types[non_matches],
                 known_types[non_matches])))
    assert not non_matches.any(), message


def get_fn(filename):
    """Gets the full path of the file name for a particular test file.

    Parameters
    ----------
    filename : str
        Name of the file to get

    Returns
    -------
    path: str
        Name of the test file with the full path location
    """
    return join(split(abspath(__file__))[0], 'files', filename)


def glob_fn(pattern):
    """Gets the full paths for test files adhering to the glob pattern.

    Parameters
    ----------
    pattern : str
        the pattern for the files(expanded using globbing)

    Returns
    -------
    list of file absolute paths matching the pattern.
    """
    return glob.glob(join(split(abspath(__file__))[0], 'files', pattern))


def register_mock_request(mocker,
                          url='http://api.crossref.org/',
                          http_verb='GET',
                          text='',
                          path=None,
                          headers=None,
                          status_code=200):
    """Registers the mocker for the given uri.

    Parameters
    ----------
    mocker : request_mock's mocker object
    url: url to register the mocker for
    http_verb: One of the many http verbs, default GET
    text: the fake text response, default ''
    path: (str) path of the resource that forms the uri, default None
    headers: (dict) the http headers to match (optional), default None
    status_code: (int), the status code of the response, default 200
    """
    uri = url
    if headers is None:
        headers = {}
    if path is not None:
        uri = parseurl.urljoin(url, path, allow_fragments=False)
    mocker.register_uri(http_verb, uri, headers=headers, text=text, status_code=status_code)