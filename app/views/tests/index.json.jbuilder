json.array!(@tests) do |test|
  json.extract! test, :id, :version_id, :user_id, :compatibility, :comment
  json.url test_url(test, format: :json)
end
