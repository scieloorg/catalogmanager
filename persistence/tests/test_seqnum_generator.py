
def test_sequential_number_zero(seqnumber_generator):
    assert seqnumber_generator.get()['SEQ'] == 0


def test_sequential_number_new(seqnumber_generator):
    expected = seqnumber_generator.get()['SEQ']
    seqnumber_generator.new() == expected + 1


def test_sequential_number_new_3(seqnumber_generator):
    assert seqnumber_generator.get()['SEQ'] == 0
    assert seqnumber_generator.get()['SEQ'] == 0
    assert seqnumber_generator.new() == 1
    assert seqnumber_generator.get()['SEQ'] == 1
    assert seqnumber_generator.new() == 2
    assert seqnumber_generator.get()['SEQ'] == 2
    assert seqnumber_generator.new() == 3
    assert seqnumber_generator.get()['SEQ'] == 3
