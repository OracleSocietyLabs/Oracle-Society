
// MIT-licensed minimal SerializableDictionary for Unity
using System;
using System.Collections.Generic;
using UnityEngine;

[Serializable]
public class SerializableDictionary<TKey, TValue> : Dictionary<TKey, TValue>, ISerializationCallbackReceiver
{
    [SerializeField] private List<TKey> _keys = new();
    [SerializeField] private List<TValue> _values = new();

    public SerializableDictionary() : base() {}
    public SerializableDictionary(IDictionary<TKey,TValue> other) : base(other) {}

    public void OnBeforeSerialize() {
        _keys.Clear(); _values.Clear();
        foreach (var kv in this) { _keys.Add(kv.Key); _values.Add(kv.Value); }
    }

    public void OnAfterDeserialize() {
        this.Clear();
        int n = Math.Min(_keys.Count, _values.Count);
        for (int i=0;i<n;i++) this[_keys[i]] = _values[i];
    }
}
