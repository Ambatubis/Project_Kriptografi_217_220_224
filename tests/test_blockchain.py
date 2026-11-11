from blockchain.chain import Blockchain
from database.db import Database
from database.repository import BlockchainRepository


def make():
    db = Database(":memory:")
    return db, Blockchain(BlockchainRepository(db))


def test_genesis_and_link():
    _, c = make()
    c.add_block("a"); c.add_block("b")
    b = c.blocks()
    assert len(b) == 3 and b[1].previous_hash == b[0].current_hash and b[2].previous_hash == b[1].current_hash
    assert c.verify()[0]


def test_detect_data_tamper():
    db, c = make()
    c.add_block("a"); c.add_block("b")
    db.execute("UPDATE blockchain_records SET data='HACKED' WHERE block_index=1")
    ok, idx, _ = c.verify()
    assert not ok and idx == 1


def test_detect_broken_link():
    db, c = make()
    c.add_block("a"); c.add_block("b")
    db.execute("UPDATE blockchain_records SET previous_hash='x' WHERE block_index=2")
    ok, idx, _ = c.verify()
    assert not ok and idx == 2
