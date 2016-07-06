class AddTestedAtToTests < ActiveRecord::Migration
  def change
    add_column :tests, :tested_at, :string
  end
end
