
def test_sequential_number_zero(seqnumber_generator):
    assert seqnumber_generator.get()['SEQ'] == 0


def test_sequential_number_new(seqnumber_generator):
    expected = seqnumber_generator.get()['SEQ']
    seqnumber_generator.new() == expected + 1


def test_sequential_number_new_3(seqnumber_generator):
    assert 0 == seqnumber_generator.get()['SEQ']
    assert 1 == seqnumber_generator.new()
    assert 1 == seqnumber_generator.get()['SEQ']
    assert 2 == seqnumber_generator.new()
    assert 2 == seqnumber_generator.get()['SEQ']
    assert 3 == seqnumber_generator.new()
    assert seqnumber_generator.get()['SEQ'] == 3


def test_sequential_number_rollback(seqnumber_generator):
    assert 0 == seqnumber_generator.get()['SEQ']
    assert 1 == seqnumber_generator.new()
    assert 1 == seqnumber_generator.get()['SEQ']
    assert 2 == seqnumber_generator.new()
    assert 2 == seqnumber_generator.get()['SEQ']
    assert 3 == seqnumber_generator.new()
    seqnumber_generator.rollback()
    assert seqnumber_generator.get()['SEQ'] == 2
