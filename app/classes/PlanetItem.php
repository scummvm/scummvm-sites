<?php

/**
 * Planet item
 */

class PlanetItem extends SimplePie_Item
{
    public function __construct($feed, $data)
    {
        parent::__construct($feed, $data);
    }

    /**
     * Gets the author name, with some logic to extract a name from a RSS feed
     * author tag
     * @param int $key
     * @return string|null
     */
    public function get_author_name($key = 0) {
      $author = $this->get_author($key);

      if (!$author) {
        return null;
      }

      if ($author->get_name()) {
        return $author->get_name();
      }

      if ($author->get_email()) {
        // Remove email address and parentheses
        $name = preg_replace('/(\S*@\S*\s?)|\(|\)/', '', $author->get_email());
        if ($name) {
          return $name;
        }
      }

      return 'Unknown';
    }

    /**
     * @param PlanetItem $item1
     * @param PlanetItem $item2
     * @return int
     */
    public static function compare($item1, $item2)
    {
        $item1_date = $item1->get_date('U');
        $item2_date = $item2->get_date('U');

        if ($item1_date == $item2_date) {
            return 0;
        } elseif ($item1_date < $item2_date) {
            return 1;
        }

        return -1;
    }
}
